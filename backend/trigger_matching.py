from app import create_app, db
from app.tasks import calculate_matches_task
from app.models import JobMatch, Job

app = create_app()

with app.app_context():
    print("Triggering Matching Task...")
    try:
        # Call directly (synchronous)
        result = calculate_matches_task()
        print(f"Task result: {result}")
        
        # Verify matches
        matches = JobMatch.query.order_by(JobMatch.score.desc()).limit(5).all()
        print(f"\nTop {len(matches)} Matches:")
        for m in matches:
            job = Job.query.get(m.job_id)
            print(f"- Job: {job.title} | Score: {m.score}")
            print(f"  Breakdown: {m.breakdown}")
            
    except Exception as e:
        with open('error.log', 'w') as f:
            f.write(f"Error: {e}\n")
            import traceback
            traceback.print_exc(file=f)
        print("Error occurred. Check error.log")
