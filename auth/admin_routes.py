"""
Evident Admin Panel Routes  
Dashboard, user management, system monitoring
"""

from datetime import datetime, timedelta
from functools import wraps

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import func, desc, extract

from auth.models import db, User, UserRole, TierLevel, AuditLog, UsageRecord, admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def get_client_ip():
    """Get client IP address"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr


# ============================================================================
# Dashboard Routes
# ============================================================================

@admin_bp.route('/', methods=['GET'])
@login_required
@admin_required
def dashboard():
    """Admin dashboard overview"""
    # Get statistics
    total_users = User.query.filter_by(is_deleted=False).count()
    active_users = User.query.filter_by(is_deleted=False, is_active=True).count()
    verified_users = User.query.filter_by(is_deleted=False, is_verified=True).count()
    
    # Tier breakdown
    tier_breakdown = db.session.query(
        User.tier,
        func.count(User.id).label('count')
    ).filter_by(is_deleted=False).group_by(User.tier).all()
    
    tier_breakdown_dict = {tier.value: count for tier, count in tier_breakdown}
    
    # Recent activity
    recent_actions = AuditLog.query.order_by(desc(AuditLog.created_at)).limit(10).all()
    
    # User registration trend (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    daily_registrations = db.session.query(
        func.date(User.created_at).label('date'),
        func.count(User.id).label('count')
    ).filter(User.created_at >= seven_days_ago).group_by(func.date(User.created_at)).all()
    
    registration_data = [count for _, count in sorted(daily_registrations)]
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'verified_users': verified_users,
        'tier_breakdown': tier_breakdown_dict,
        'recent_actions': recent_actions,
        'registration_data': registration_data,
    }
    
    return render_template('admin/dashboard.html', **context)


# ============================================================================
# User Management Routes
# ============================================================================

@admin_bp.route('/users', methods=['GET', 'POST'])
@login_required
@admin_required
def users_list():
    """List and manage users"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    search = request.args.get('search', '').strip()
    tier_filter = request.args.get('tier', '')
    role_filter = request.args.get('role', '')
    status_filter = request.args.get('status', '')
    
    query = User.query.filter_by(is_deleted=False)
    
    # Search
    if search:
        query = query.filter(
            db.or_(
                User.email.ilike(f'%{search}%'),
                User.username.ilike(f'%{search}%'),
                User.full_name.ilike(f'%{search}%'),
            )
        )
    
    # Filters
    if tier_filter:
        try:
            query = query.filter_by(tier=TierLevel[tier_filter.upper()])
        except KeyError:
            pass
    
    if role_filter:
        try:
            query = query.filter_by(role=UserRole[role_filter.upper()])
        except KeyError:
            pass
    
    if status_filter == 'active':
        query = query.filter_by(is_active=True)
    elif status_filter == 'inactive':
        query = query.filter_by(is_active=False)
    elif status_filter == 'unverified':
        query = query.filter_by(is_verified=False)
    
    # Pagination
    users = query.order_by(desc(User.created_at)).paginate(page=page, per_page=per_page)
    
    return render_template(
        'admin/users_list.html',
        users=users,
        search=search,
        tier_filter=tier_filter,
        role_filter=role_filter,
        status_filter=status_filter,
    )


@admin_bp.route('/users/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit specific user"""
    user = User.query.filter_by(id=user_id, is_deleted=False).first_or_404()
    
    if request.method == 'POST':
        try:
            user.full_name = request.form.get('full_name', user.full_name)
            user.organization = request.form.get('organization', user.organization)
            user.role = UserRole[request.form.get('role', user.role.name)]
            user.tier = TierLevel[request.form.get('tier', user.tier.name)]
            user.is_active = request.form.get('is_active', 'off') == 'on'
            user.is_verified = request.form.get('is_verified', 'off') == 'on'
            
            db.session.commit()
            
            current_user.log_action(
                'admin_user_updated',
                {'user_id': user_id, 'user_email': user.email},
                get_client_ip()
            )
            
            flash(f'✅ User {user.email} updated successfully', 'success')
            return redirect(url_for('admin.edit_user', user_id=user_id))
        except (KeyError, ValueError) as e:
            db.session.rollback()
            flash(f'❌ Update failed: {str(e)}', 'danger')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Admin user edit error: {str(e)}")
            flash(f'❌ Error: {str(e)}', 'danger')
    
    # Get user's recent activity
    recent_activity = AuditLog.query.filter_by(user_id=user_id).order_by(
        desc(AuditLog.created_at)
    ).limit(20).all()
    
    return render_template(
        'admin/edit_user.html',
        user=user,
        recent_activity=recent_activity,
        roles=[r.value for r in UserRole],
        tiers=[t.value for t in TierLevel],
    )


@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    user = User.query.filter_by(id=user_id, is_deleted=False).first_or_404()
    
    # Prevent self-disable
    if user_id == current_user.id:
        return jsonify({'success': False, 'error': 'Cannot disable your own account'}), 400
    
    user.is_active = not user.is_active
    db.session.commit()
    
    current_user.log_action(
        'admin_user_status_toggled',
        {'user_id': user_id, 'new_status': user.is_active},
        get_client_ip()
    )
    
    status = 'enabled' if user.is_active else 'disabled'
    flash(f'✅ User {user.email} has been {status}', 'success')
    
    return jsonify({
        'success': True,
        'message': f'User {status}',
        'is_active': user.is_active,
    })


@admin_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
@admin_required
def reset_user_password(user_id):
    """Admin reset user password"""
    user = User.query.filter_by(id=user_id, is_deleted=False).first_or_404()
    
    temp_password = secrets.token_urlsafe(12)
    user.set_password(temp_password)
    db.session.commit()
    
    current_user.log_action(
        'admin_password_reset',
        {'user_id': user_id, 'user_email': user.email},
        get_client_ip()
    )
    
    flash(f'✅ Password reset. Temporary password: {temp_password}', 'success')
    
    # TODO: Send email to user with temporary password
    
    return jsonify({'success': True, 'temp_password': temp_password})


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Soft-delete user account"""
    user = User.query.filter_by(id=user_id, is_deleted=False).first_or_404()
    
    # Prevent self-delete
    if user_id == current_user.id:
        return jsonify({'success': False, 'error': 'Cannot delete your own account'}), 400
    
    user.is_deleted = True
    user.is_active = False
    db.session.commit()
    
    current_user.log_action(
        'admin_user_deleted',
        {'user_id': user_id, 'user_email': user.email},
        get_client_ip()
    )
    
    flash(f'✅ User {user.email} has been deleted', 'success')
    return redirect(url_for('admin.users_list'))


import secrets  # Add to imports


# ============================================================================
# API Endpoints for Admin Operations
# ============================================================================

@admin_bp.route('/api/stats', methods=['GET'])
@login_required
@admin_required
def api_stats():
    """Get admin statistics"""
    total_users = User.query.filter_by(is_deleted=False).count()
    active_users = User.query.filter_by(is_deleted=False, is_active=True).count()
    verified_users = User.query.filter_by(is_deleted=False, is_verified=True).count()
    
    tier_breakdown = db.session.query(
        User.tier,
        func.count(User.id).label('count')
    ).filter_by(is_deleted=False).group_by(User.tier).all()
    
    tier_breakdown_dict = {tier.value: count for tier, count in tier_breakdown}
    
    return jsonify({
        'total_users': total_users,
        'active_users': active_users,
        'verified_users': verified_users,
        'tier_breakdown': tier_breakdown_dict,
        'timestamp': datetime.utcnow().isoformat(),
    })


@admin_bp.route('/api/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
@admin_required
def api_user(user_id):
    """User API endpoint"""
    user = User.query.filter_by(id=user_id, is_deleted=False).first_or_404()
    
    if request.method == 'GET':
        return jsonify({'user': user.to_dict(include_sensitive=True)})
    
    elif request.method == 'PUT':
        data = request.get_json()
        
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'tier' in data:
            user.tier = TierLevel[data['tier'].upper()]
        if 'role' in data:
            user.role = UserRole[data['role'].upper()]
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        db.session.commit()
        current_user.log_action('admin_user_updated_api', {'user_id': user_id}, get_client_ip())
        
        return jsonify({'success': True, 'user': user.to_dict()})
    
    elif request.method == 'DELETE':
        if user_id == current_user.id:
            return jsonify({'success': False, 'error': 'Cannot delete your own account'}), 400
        
        user.is_deleted = True
        db.session.commit()
        current_user.log_action('admin_user_deleted_api', {'user_id': user_id}, get_client_ip())
        
        return jsonify({'success': True, 'message': 'User deleted'})


@admin_bp.route('/api/audit-logs', methods=['GET'])
@login_required
@admin_required
def api_audit_logs():
    """Get audit logs"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    user_id = request.args.get('user_id', type=int)
    action_filter = request.args.get('action', '')
    
    query = AuditLog.query
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    if action_filter:
        query = query.filter(AuditLog.action.like(f'%{action_filter}%'))
    
    logs = query.order_by(desc(AuditLog.created_at)).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'total': logs.total,
        'pages': logs.pages,
        'current_page': page,
        'logs': [log.to_dict() for log in logs.items],
    })
