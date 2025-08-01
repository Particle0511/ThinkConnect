from functools import wraps
from flask import render_template, flash, redirect, url_for, request, abort
from flask.blueprints import Blueprint
from flask_login import login_user, current_user, logout_user, login_required

from . import db
from .forms import CommentForm, IssueForm, LoginForm, RegistrationForm
from .models import Comment, Issue, User, Booking


main = Blueprint('main', __name__)


def role_required(role_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if (
                not current_user.is_authenticated or
                current_user.role != role_name
            ):
                flash('This page is for administrators only.', 'danger')
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@main.route('/')
@main.route('/index')
def index():
    issues = Issue.query.order_by(Issue.date_posted.desc()).limit(5).all()
    return render_template('index.html', issues=issues)


@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))
        else:
            flash(
                'Login Unsuccessful. Please check email and password',
                'danger'
            )
    return render_template('login.html', title='Login', form=form)


@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(
            'Your account has been created! You are now able to log in',
            'success')
        return redirect(url_for('main.login'))
    return render_template('signup.html', title='Sign Up', form=form)


@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@main.route('/dashboard')
@login_required
def dashboard():
    user_issues = (
        Issue.query.filter_by(author=current_user)
        .order_by(Issue.date_posted.desc())
        .all()
    )
    return render_template(
        'dashboard.html', title='Dashboard', issues=user_issues)


@main.route('/issues')
def issues():
    all_issues = Issue.query.order_by(Issue.date_posted.desc()).all()
    return render_template(
        'issues.html', title='All Issues', issues=all_issues)


@main.route('/issue/<int:issue_id>', methods=['GET', 'POST'])
def issue_details(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    form = CommentForm()

    user_has_booked = False
    if current_user.is_authenticated:
        user_booking = Booking.query.filter_by(
            user_id=current_user.id, issue_id=issue.id).first()
        if user_booking:
            user_has_booked = True

    booked_slots = Booking.query.filter_by(issue_id=issue.id).count()
    remaining_slots = issue.total_slots - booked_slots

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('You must be logged in to comment.', 'info')
            return redirect(url_for('main.login'))
        comment = Comment(
            content=form.content.data, author=current_user, parent_issue=issue)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been published.', 'success')
        return redirect(url_for('main.issue_details', issue_id=issue.id))

    comments = (
        Comment.query.filter_by(issue_id=issue.id)
        .order_by(Comment.date_posted.asc())
        .all()
    )
    return render_template(
        'issue_details.html', title=issue.title, form=form, issue=issue,
        comments=comments, remaining_slots=remaining_slots,
        user_has_booked=user_has_booked)


@main.route('/post_issue', methods=['GET', 'POST'])
@login_required
def post_issue():
    form = IssueForm()
    if form.validate_on_submit():
        issue = Issue(
            title=form.title.data,
            description=form.description.data,
            category=form.category.data,
            author=current_user,
            total_slots=form.total_slots.data,
            mode=form.mode.data
        )
        db.session.add(issue)
        db.session.commit()
        flash('Your issue has been posted!', 'success')
        return redirect(url_for('main.issue_details', issue_id=issue.id))
    return render_template('post_issue.html', title='New Issue', form=form)


@main.route('/book_slot/<int:issue_id>', methods=['POST'])
@login_required
def book_slot(issue_id):
    issue = Issue.query.get_or_404(issue_id)

    existing_booking = Booking.query.filter_by(
        user_id=current_user.id, issue_id=issue.id).first()
    if existing_booking:
        flash('You have already booked a slot for this event.', 'info')
        return redirect(url_for('main.issue_details', issue_id=issue.id))

    booked_slots = Booking.query.filter_by(issue_id=issue.id).count()
    if booked_slots >= issue.total_slots:
        flash('Sorry, all slots for this event are booked.', 'danger')
        return redirect(url_for('main.issue_details', issue_id=issue.id))

    new_booking = Booking(user_id=current_user.id, issue_id=issue.id)
    db.session.add(new_booking)
    db.session.commit()
    flash('Your slot has been successfully booked!', 'success')
    return redirect(url_for('main.issue_details', issue_id=issue.id))


@main.route('/issue/<int:issue_id>/delete', methods=['POST'])
@login_required
def delete_issue(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    if issue.author != current_user:
        abort(403)
    db.session.delete(issue)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.issues'))


@main.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('profile.html', user=user)


@main.route('/about')
def about():
    return render_template('about.html', title='About')


@main.route('/contact')
def contact():
    return render_template('contact.html', title='Contact')


@main.route('/admin')
@login_required
@role_required('admin')
def admin():
    users = User.query.order_by(User.created_at.desc()).all()
    user_count = User.query.count()
    issue_count = Issue.query.count()
    return render_template(
        'admin.html', title='Admin Panel', users=users,
        user_count=user_count, issue_count=issue_count)

