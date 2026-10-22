import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import query_db, execute_db

def generate_personalized_remediation(student_id, target_tier='Tier 1 Product'):
    """
    Analyzes student metrics, SHAP negatives, and drive deficits to construct
    an individualized, actionable study roadmap & engineering action plan.
    """
    student = query_db("SELECT * FROM students WHERE id = ?", (student_id,), one=True)
    if not student:
        raise ValueError("Student not found")

    dsa_score = float(student['dsa_score'])
    leetcode = int(student['leetcode_solved'])
    projects = int(student['projects_count'])
    backlogs = int(student['active_backlogs'])
    soft_skills = float(student['soft_skills_score'] if student.get('soft_skills_score') is not None else 0.0)

    # 1. Diagnose specific skill deficiencies
    weaknesses = []
    if dsa_score < 75.0 or leetcode < 200:
        gap = max(0, 250 - leetcode)
        weaknesses.append({
            'area': 'Data Structures & Algorithmic Problem Solving',
            'severity': 'High' if dsa_score < 60 else 'Medium',
            'metric': f"Current Score: {dsa_score:.1f}/100, LeetCode: {leetcode} solved",
            'deficiency': f"Need ~{gap} more algorithmic problems solved to qualify comfortably for {target_tier} coding rounds."
        })

    if projects < 3:
        weaknesses.append({
            'area': 'Full-Stack / Distributed Systems Projects',
            'severity': 'High' if projects < 2 else 'Medium',
            'metric': f"{projects} completed projects",
            'deficiency': f"Recruiters expect at least 3 production-grade, deployed portfolio projects with clean Git repositories."
        })

    if backlogs > 0:
        weaknesses.append({
            'area': 'Academic Remediation',
            'severity': 'Critical',
            'metric': f"{backlogs} active backlogs",
            'deficiency': "Most Tier 1 & Tier 2 companies strictly enforce a 0 active backlog policy at the time of online assessment."
        })

    if soft_skills < 75.0:
        weaknesses.append({
            'area': 'Interview Fluency & Vocal Projection',
            'severity': 'Medium',
            'metric': f"Soft skills score: {soft_skills:.1f}/100",
            'deficiency': "Candidate exhibits hesitations or fast cadence during speech delivery."
        })

    # 2. Tailored DSA Roadmap (4-Week Intensive Sprint)
    dsa_plan = [
        {
            'week': 'Week 1',
            'focus': 'Arrays, Two Pointers & Sliding Window',
            'target_count': '15 Problems',
            'key_problems': ['Container With Most Water', 'Trapping Rain Water', 'Minimum Window Substring', '3Sum'],
            'resource': 'NeetCode 150 - Sliding Window & Two Pointers'
        },
        {
            'week': 'Week 2',
            'focus': 'Binary Trees, BST & Trie',
            'target_count': '18 Problems',
            'key_problems': ['Lowest Common Ancestor', 'Serialize & Deserialize Binary Tree', 'Word Search II', 'Validate BST'],
            'resource': 'Striver SDE Sheet - Trees & Traversal Module'
        },
        {
            'week': 'Week 3',
            'focus': 'Graphs, BFS/DFS & Shortest Path (Dijkstra)',
            'target_count': '15 Problems',
            'key_problems': ['Course Schedule I & II', 'Network Delay Time', 'Word Ladder', 'Rotting Oranges'],
            'resource': 'Algorithms by Sedgewick & LeetCode Graph Theory Card'
        },
        {
            'week': 'Week 4',
            'focus': 'Dynamic Programming & System Design Basics',
            'target_count': '15 Problems',
            'key_problems': ['Longest Increasing Subsequence', 'Coin Change', 'Word Break', 'Edit Distance'],
            'resource': 'Grokking the System Design Interview & DP Patterns'
        }
    ]

    # 3. Project Recommendations matching Target Tier
    project_ideas = []
    if target_tier == 'Tier 1 Product':
        project_ideas = [
            {
                'title': 'High-Throughput Distributed Rate Limiter & Token Bucket',
                'tech_stack': 'Go / Python, Redis, Docker, gRPC',
                'description': 'Implement sliding-window counter and token bucket algorithms with Redis cluster synchronization.',
                'resume_impact': 'Demonstrates concurrency, distributed caching, and backend scalability for Product companies.'
            },
            {
                'title': 'Real-Time Collaborative Code Editor with CRDT / WebSockets',
                'tech_stack': 'Python FastAPI / Node.js, WebSockets, Redis Pub/Sub, React',
                'description': 'Real-time collaborative editing using Conflict-free Replicated Data Types (CRDTs) and operational transformation.',
                'resume_impact': 'Demonstrates network protocol mastery and complex state synchronization.'
            }
        ]
    else:
        project_ideas = [
            {
                'title': 'Microservices E-Commerce Order & Payment Pipeline',
                'tech_stack': 'Python Flask / FastAPI, MySQL, RabbitMQ / Celery, Docker',
                'description': 'Decoupled services for catalog, cart, and payment handling with transaction rollbacks and database locking.',
                'resume_impact': 'Directly matches core industry development stacks sought by Enterprise recruiters.'
            },
            {
                'title': 'Secure Role-Based Campus Asset Management Portal',
                'tech_stack': 'Python, MySQL 3NF Schema, JWT, TailwindCSS',
                'description': 'Full relational database modeling with audit logs, foreign keys, and PDF report generators.',
                'resume_impact': 'Shows enterprise relational database competence and secure software design.'
            }
        ]

    # 4. Mock Interview & Soft-Skills Drills
    interview_drills = [
        {
            'topic': 'STAR Technical Explanation Drill',
            'prompt': 'Describe the most complex architectural bug you encountered in a recent project and how you resolved it.',
            'tip': 'Spend 20% time on Situation/Task, 50% on technical Action taken, and 30% on quantifiable Results.'
        },
        {
            'topic': 'System Trade-offs Verbalization',
            'prompt': 'Why would you choose an RDBMS (MySQL) over a NoSQL database for transactional financial ledgers?',
            'tip': 'Speak clearly about ACID guarantees, foreign keys, and normalization benefits with steady pacing (130-150 WPM).'
        },
        {
            'topic': 'HR Behavioral & Core Alignment',
            'prompt': 'Tell me about a time you had a technical disagreement with a teammate. How was it resolved?',
            'tip': 'Emphasize data-driven consensus, empathy, and collective project velocity.'
        }
    ]

    return {
        'student': student,
        'target_tier': target_tier,
        'weaknesses': weaknesses,
        'dsa_plan': dsa_plan,
        'project_ideas': project_ideas,
        'interview_drills': interview_drills
    }

if __name__ == '__main__':
    remediation = generate_personalized_remediation(4, 'Tier 1 Product')
    print("Identified Weaknesses for Arpit Tale:")
    for w in remediation['weaknesses']:
        print(f" - [{w['severity']}] {w['area']}: {w['deficiency']}")
    print("\nDSA Plan Weeks:", len(remediation['dsa_plan']))
    print("Project Recommendations:", len(remediation['project_ideas']))
