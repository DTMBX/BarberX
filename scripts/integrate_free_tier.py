# Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
# PROPRIETARY — See LICENSE.

"""
FREE Tier Integration Script
Automatically integrates FREE tier functionality into main app
"""

import os
import sys


def integrate_free_tier():
    """Integrate FREE tier modules into app.py"""

    print("=" * 70)
    print("FREE TIER INTEGRATION")
    print("=" * 70)

    # Read current app.py
    with open("app.py", encoding="utf-8") as f:
        app_content = f.read()

    # Check if already integrated
    if "free_tier_demo_cases" in app_content:
        print("✅ FREE tier already integrated!")
        return True

    print("\n📝 Adding imports...")

    # Imports to add
    new_imports = """
# FREE Tier Functionality
from free_tier_demo_cases import get_demo_cases, get_demo_case_by_id, is_demo_case
from free_tier_educational_resources import get_all_educational_resources, get_resource_by_id, CATEGORIES
from free_tier_upload_manager import OneTimeUploadManager, free_tier_upload_route_decorator
from free_tier_data_retention import get_user_data_status, DataRetentionManager
from free_tier_watermark import WatermarkService
"""

    # Find the imports section (after other imports)
    import_marker = "from flask import Flask"
    if import_marker in app_content:
        parts = app_content.split(import_marker, 1)
        app_content = (
            parts[0]
            + import_marker
            + parts[1].split("\n", 1)[0]
            + "\n"
            + new_imports
            + "\n"
            + parts[1].split("\n", 1)[1]
        )

    print("✅ Imports added")

    print("\n📝 Adding FREE tier routes...")

    # Routes to add
    new_routes = """

# ============================================================================
# FREE TIER ROUTES
# ============================================================================

@app.route('/free-dashboard')
@login_required
def free_dashboard():
    \"\"\"FREE tier dashboard with demo cases and educational resources\"\"\"
    from flask_login import current_user
    from models_auth import TierLevel
    
    # Redirect non-FREE users to regular dashboard
    if current_user.tier != TierLevel.FREE:
        return redirect(url_for('dashboard'))
    
    # Get demo cases
    demo_cases = get_demo_cases()
    
    # Get educational resources
    educational_resources = get_all_educational_resources()
    
    # Get upload status
    upload_status = OneTimeUploadManager.get_upload_status(current_user)
    
    # Get data retention status
    data_status = get_user_data_status(current_user)
    
    return render_template('free_tier_dashboard.html',
                         demo_cases=demo_cases,
                         educational_resources=educational_resources,
                         upload_status=upload_status,
                         data_status=data_status)


@app.route('/cases/<case_id>')
@login_required
def view_case(case_id):
    \"\"\"View case details (handles both demo and real cases)\"\"\"
    from flask_login import current_user
    
    # Check if it's a demo case
    if is_demo_case(case_id):
        demo_case = get_demo_case_by_id(case_id)
        if not demo_case:
            flash('Demo case not found', 'error')
            return redirect(url_for('free_dashboard'))
        
        return render_template('demo_case_detail.html', case=demo_case)
    
    # Regular case logic here
    # case = Case.query.get_or_404(case_id)
    # return render_template('case_detail.html', case=case)
    
    flash('Case viewing coming soon', 'info')
    return redirect(url_for('free_dashboard'))


@app.route('/education')
@app.route('/education/<category>')
@login_required
def education_center(category=None):
    \"\"\"Educational resources center\"\"\"
    resources = get_all_educational_resources()
    
    return render_template('education_center.html',
                         resources=resources,
                         categories=CATEGORIES,
                         selected_category=category)


@app.route('/education/resource/<resource_id>')
@login_required
def view_resource(resource_id):
    \"\"\"View specific educational resource\"\"\"
    resource = get_resource_by_id(resource_id)
    
    if not resource:
        flash('Resource not found', 'error')
        return redirect(url_for('education_center'))
    
    return render_template('resource_detail.html', resource=resource)


@app.route('/api/upload-status')
@login_required
def get_upload_status():
    \"\"\"API endpoint for upload status\"\"\"
    from flask import jsonify
    from flask_login import current_user
    
    status = OneTimeUploadManager.get_upload_status(current_user)
    return jsonify(status)


@app.route('/api/data-retention-status')
@login_required
def get_data_retention_status():
    \"\"\"API endpoint for data retention status\"\"\"
    from flask import jsonify
    from flask_login import current_user
    
    status = get_user_data_status(current_user)
    return jsonify(status)


# ============================================================================
# END FREE TIER ROUTES
# ============================================================================
"""

    # Add routes before the last line (if __name__ == "__main__")
    if 'if __name__ == "__main__"' in app_content:
        parts = app_content.split('if __name__ == "__main__"')
        app_content = parts[0] + new_routes + '\n\nif __name__ == "__main__"' + parts[1]
    else:
        app_content += new_routes

    print("✅ Routes added")

    # Save updated app.py
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(app_content)

    print("\n✅ Integration complete!")
    return True


def create_placeholder_templates():
    """Create placeholder templates for demo case and education center"""

    print("\n📝 Creating placeholder templates...")

    # Demo case detail template
    demo_case_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ case.title }} - Evident</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container py-5">
        <div class="alert alert-info">
            <i class="fas fa-info-circle me-2"></i>
            This is a DEMO case for educational purposes.
        </div>
        
        <h1>{{ case.title }}</h1>
        <p class="text-muted">{{ case.case_number }} • {{ case.incident_date }}</p>
        
        <div class="row mt-4">
            <div class="col-md-8">
                <h3>Description</h3>
                <p>{{ case.description }}</p>
                
                <h3 class="mt-4">Timeline</h3>
                <ul class="list-group">
                    {% for event in case.timeline %}
                    <li class="list-group-item">
                        <strong>{{ event.time }}</strong> - {{ event.event }}
                        <span class="badge bg-{{ 'danger' if event.severity == 'high' else 'warning' if event.severity == 'medium' else 'secondary' }}">
                            {{ event.severity }}
                        </span>
                    </li>
                    {% endfor %}
                </ul>
                
                <h3 class="mt-4">AI Analysis</h3>
                <div class="card">
                    <div class="card-body">
                        <h5>Constitutional Issues</h5>
                        <ul>
                            {% for issue in case.ai_analysis.constitutional_issues %}
                            <li>{{ issue }}</li>
                            {% endfor %}
                        </ul>
                        
                        <h5 class="mt-3">Policy Compliance</h5>
                        <p>{{ case.ai_analysis.policy_compliance }}</p>
                        
                        <h5 class="mt-3">Recommendations</h5>
                        <p>{{ case.ai_analysis.recommendations }}</p>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="card">
                    <div class="card-body">
                        <h5>Case Details</h5>
                        <p><strong>Type:</strong> {{ case.case_type }}</p>
                        <p><strong>Status:</strong> {{ case.status }}</p>
                        <p><strong>Risk Level:</strong> {{ case.ai_analysis.risk_level }}</p>
                    </div>
                </div>
                
                <div class="alert alert-warning mt-3">
                    <h6>Want to analyze YOUR cases?</h6>
                    <p class="small mb-2">Upgrade to STARTER for $29/mo</p>
                    <a href="/pricing" class="btn btn-sm btn-warning w-100">Upgrade Now</a>
                </div>
            </div>
        </div>
        
        <a href="/free-dashboard" class="btn btn-secondary mt-4">← Back to Dashboard</a>
    </div>
</body>
</html>
"""

    with open("templates/demo_case_detail.html", "w", encoding="utf-8") as f:
        f.write(demo_case_template)

    print("✅ Created demo_case_detail.html")

    # Education center template
    education_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Education Center - Evident</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container py-5">
        <h1>Education Center</h1>
        <p class="lead">Free resources to master legal technology</p>
        
        <div class="row mt-4">
            <div class="col-md-6">
                <h3>Guides</h3>
                {% for guide in resources.guides %}
                <div class="card mb-3">
                    <div class="card-body">
                        <h5>{{ guide.title }}</h5>
                        <p>{{ guide.description }}</p>
                        <span class="badge bg-primary">{{ guide.duration }}</span>
                    </div>
                </div>
                {% endfor %}
            </div>
            
            <div class="col-md-6">
                <h3>Templates</h3>
                {% for template in resources.templates %}
                <div class="card mb-3">
                    <div class="card-body">
                        <h5>{{ template.title }}</h5>
                        <p>{{ template.description }}</p>
                        <a href="{{ template.download_url }}" class="btn btn-sm btn-success" download>
                            Download {{ template.file_type }}
                        </a>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
</body>
</html>
"""

    with open("templates/education_center.html", "w", encoding="utf-8") as f:
        f.write(education_template)

    print("✅ Created education_center.html")


def main():
    """Main integration function"""

    # Step 1: Integrate into app.py
    if integrate_free_tier():
        print("\n✅ Step 1: App integration complete")
    else:
        print("\n❌ Step 1: App integration failed")
        return False

    # Step 2: Create templates
    create_placeholder_templates()
    print("\n✅ Step 2: Templates created")

    print("\n" + "=" * 70)
    print("✅ FREE TIER INTEGRATION COMPLETE!")
    print("=" * 70)

    print("\n📋 Next Steps:")
    print("1. Run database migration:")
    print("   python migrate_add_free_tier_uploads.py")
    print("\n2. Restart Flask app")
    print("\n3. Test FREE tier functionality:")
    print("   - Visit /free-dashboard")
    print("   - View demo cases")
    print("   - Try one-time upload")
    print("   - Check educational resources")
    print("\n4. Set up daily cron job for data cleanup:")
    print(
        '   0 3 * * * cd /var/www/Evident && python -c "from free_tier_data_retention import DataRetentionManager; DataRetentionManager.run_cleanup_job()"'
    )

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
