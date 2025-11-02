"""
Realistic database seeding for demo and system demonstration.

Creates:
- 1 UserAdmin, 1 CSRRep, 1 PersonInNeed, 1 PlatformManager
- 100 CSR Reps
- 100 PIN Users
- 3 Categories
- 100 Requests per Category (300 total)
- Shortlists + Completed Matches
- Additional clean demo data for core accounts 

All passwords: testing123!
"""

from datetime import datetime, timedelta
from random import choice
from app import create_app, db
from app.entity.user_profile import UserProfile
from app.entity.user_account import UserAccount
from app.entity.category import Category
from app.entity.request import Request
from app.entity.shortlist import Shortlist
from app.entity.match_record import MatchRecord
from app.entity.report import Report


# ------------------ NAME LISTS ------------------
CSR_NAMES = [
    "Aaron Tan", "Brandon Lee", "Caleb Lim", "Daniel Wong", "Ethan Koh",
    "Felix Chua", "Gavin Ho", "Harris Ong", "Isaac Tay", "Joel Tan",
    "Kenny Teo", "Leonard Sim", "Marcus Low", "Nicholas Ho", "Owen Chia",
    "Patrick Yeo", "Quentin Soh", "Ryan Ng", "Samuel Yip", "Tristan Goh",
    "Umar Malik", "Victor Quek", "Wesley Pang", "Xavier Lau", "Yusuf Rahman",
    "Zachary Chang"
]

PIN_NAMES = [
    "Alice Tan", "Beatrice Ho", "Cheryl Lim", "Daphne Lee", "Elaine Koh",
    "Fiona Ng", "Grace Chia", "Hannah Wong", "Irene Loh", "Jasmine Tay",
    "Kelly Sim", "Lydia Pang", "Michelle Ong", "Nicole Chua", "Olivia Soh",
    "Phoebe Ting", "Queenie Goh", "Rachel Tan", "Samantha Ng", "Tina Low",
    "Uma Devi", "Vanessa Yeo", "Wendy Tan", "Xin Yi", "Yvonne Chia",
    "Zoe Lim"
]


# ------------------ Helper Functions ------------------
def sequential_phone(i: int) -> str:
    return str(81230000 + i)


def make_user(name, email, profile, idx):
    u = UserAccount(
        name=name,
        email=email,
        profileID=profile.profileID,
        phoneNumber=sequential_phone(idx),
        age=25 + (idx % 40),
        isActive=True
    )
    u.password = "testing123!"
    db.session.add(u)
    return u


# ------------------ Seeding Logic ------------------
def reset_and_seed():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        # ---- Profiles ----
        p_admin = UserProfile(profileName="UserAdmin", description="Manages users")
        p_csr = UserProfile(profileName="CSRRep", description="CSR representative")
        p_pin = UserProfile(profileName="PersonInNeed", description="Needs assistance")
        p_pm = UserProfile(profileName="PlatformManager", description="Manages categories and reports")
        db.session.add_all([p_admin, p_csr, p_pin, p_pm])
        db.session.commit()

        # ---- Core Demo Accounts ----
        admin = make_user("Admin User", "admin@test.com", p_admin, 1)
        csr_main = make_user("CSR User", "csr@test.com", p_csr, 2)
        pin_main = make_user("PIN User", "pin@test.com", p_pin, 3)
        pm = make_user("PM User", "pm@test.com", p_pm, 4)
        db.session.commit()

        # ---- 100 CSR Users ----
        csr_users = []
        idx = 10
        for i in range(100):
            name = CSR_NAMES[i % len(CSR_NAMES)] + f" {i+1:03d}"
            csr_users.append(make_user(name, f"csr{i+1:03d}@test.com", p_csr, idx))
            idx += 1

        # ---- 100 PIN Users ----
        pin_users = []
        for i in range(100):
            name = PIN_NAMES[i % len(PIN_NAMES)] + f" {i+1:03d}"
            pin_users.append(make_user(name, f"pin{i+1:03d}@test.com", p_pin, idx))
            idx += 1

        db.session.commit()

        # ---- Categories ----
        c1 = Category(categoryName="Transportation", description="Transport help", isActive=True)
        c2 = Category(categoryName="Medical Aid", description="Medical assistance", isActive=True)
        c3 = Category(categoryName="Food Support", description="Food support & groceries", isActive=True)
        db.session.add_all([c1, c2, c3])
        db.session.commit()

        categories = [c1, c2, c3]
        all_requests = []
        now = datetime.utcnow()

        # ---- Generate 100 Requests per Category ----
        for cat in categories:
            for i in range(100):
                pin = pin_users[(i + cat.categoryID) % len(pin_users)]
                created = now - timedelta(days=(i % 30))
                r = Request(
                    pinID=pin.userID,
                    categoryID=cat.categoryID,
                    title=f"{cat.categoryName} Request {i+1}",
                    description=f"Description for {cat.categoryName} request {i+1}",
                    status="open",
                    viewCount=(i % 7) + 1,
                    shortlistCount=0,
                    createdAt=created
                )
                db.session.add(r)
                all_requests.append(r)

        db.session.flush()

        # ---- Shortlists + Matches ----
        match_records = []
        for i, r in enumerate(all_requests):
            if i % 2 == 0:
                csr = csr_users[i % len(csr_users)]
                db.session.add(Shortlist(csrRepID=csr.userID, requestID=r.requestID))
                r.shortlistCount += 1

            if i % 3 == 0:
                r.status = "closed"
                completed = r.createdAt + timedelta(days=1)
                r.closedAt = completed
                csr = csr_users[(i * 7) % len(csr_users)]
                match_records.append(
                    MatchRecord(
                        requestID=r.requestID,
                        csrRepID=csr.userID,
                        pinID=r.pinID,
                        categoryID=r.categoryID,
                        status="completed",
                        matchedAt=r.createdAt + timedelta(hours=3),
                        completedAt=completed
                    )
                )

        db.session.add_all(match_records)
        db.session.commit()

        # ---------------------------------------------------------
        # ADD CLEAN DEMO DATA FOR CORE ACCOUNTS 
        # ---------------------------------------------------------
        demo_titles = [
            "Wheelchair-accessible transport needed",
            "Groceries delivery support",
            "Medical appointment follow-up transport",
            "Assistance with weekly food run",
            "Support for clinic visit transportation"
        ]

        demo_descriptions = [
            "Requesting assistance due to mobility issues.",
            "Regular grocery support needed for 4 weeks.",
            "Follow-up appointment scheduled, require lift assistance.",
            "Need weekly help to collect groceries from NTUC.",
            "Transportation support required for medical visit."
        ]

        demo_requests = []
        for i in range(5):
            created_date = now - timedelta(days=(5 - i))
            r = Request(
                pinID=pin_main.userID,
                categoryID=choice(categories).categoryID,
                title=demo_titles[i],
                description=demo_descriptions[i],
                status="open",
                viewCount=0,
                shortlistCount=0,
                createdAt=created_date,
            )
            db.session.add(r)
            demo_requests.append(r)

        db.session.flush()

        for r in demo_requests:
            db.session.add(Shortlist(csrRepID=csr_main.userID, requestID=r.requestID))
            r.shortlistCount = 1

        completed_1 = demo_requests[0]
        completed_2 = demo_requests[1]

        completed_1.status = "closed"
        completed_2.status = "closed"

        completed_1.closedAt = completed_1.createdAt + timedelta(days=1)
        completed_2.closedAt = completed_2.createdAt + timedelta(days=2)

        m1 = MatchRecord(
            requestID=completed_1.requestID,
            csrRepID=csr_main.userID,
            pinID=pin_main.userID,
            categoryID=completed_1.categoryID,
            status="completed",
            matchedAt=completed_1.createdAt + timedelta(hours=3),
            completedAt=completed_1.closedAt
        )

        m2 = MatchRecord(
            requestID=completed_2.requestID,
            csrRepID=csr_main.userID,
            pinID=pin_main.userID,
            categoryID=completed_2.categoryID,
            status="completed",
            matchedAt=completed_2.createdAt + timedelta(hours=4),
            completedAt=completed_2.closedAt
        )

        db.session.add_all([m1, m2])
        db.session.commit()

        print("\nDatabase seeded successfully with realistic data.")
        print(" Login Accounts:")
        print(" admin@test.com / testing123!")
        print(" csr@test.com   / testing123!")
        print(" pin@test.com   / testing123!")
        print(" pm@test.com    / testing123!")
        print("\n Additional Test Users:")
        print(" csr001@test.com .. csr100@test.com")
        print(" pin001@test.com .. pin100@test.com")
        print("\n Core Accounts Now Have Visible Demo Requests, Shortlists & Completed Records.")


if __name__ == "__main__":
    reset_and_seed()
