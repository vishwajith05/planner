from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime
import uuid
import random
import string

from backend.app.models.friendship import (
    Friendship, SharedChallenge, ChallengeParticipant,
    EncouragementMessage, FocusTogetherSession, FocusSessionParticipant
)
from backend.app.models.user import User
from backend.app.schemas.friendship import (
    FriendRequest, ChallengeCreate, ChallengeProgressUpdate,
    EncouragementCreate, FocusSessionCreate
)


class FriendService:

    # ── Friend Discovery & Requests ─────────────────────────────────────────

    def search_users(self, db: Session, query: str, current_user_id: str) -> List[dict]:
        """Search users by email or name (excluding current user)."""
        users = db.query(User).filter(
            User.id != current_user_id,
            User.is_active == True,
            or_(
                User.email.ilike(f"%{query}%"),
                User.full_name.ilike(f"%{query}%")
            )
        ).limit(20).all()

        result = []
        for u in users:
            friendship = db.query(Friendship).filter(
                or_(
                    and_(Friendship.requester_id == current_user_id, Friendship.addressee_id == u.id),
                    and_(Friendship.requester_id == u.id, Friendship.addressee_id == current_user_id)
                )
            ).first()

            result.append({
                "id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "bio": u.bio,
                "friendship_status": friendship.status if friendship else None,
                "friendship_id": friendship.id if friendship else None
            })
        return result

    def send_friend_request(self, db: Session, requester_id: str, req: FriendRequest) -> Friendship:
        """Send a friend request to a user by email."""
        addressee = db.query(User).filter(User.email == req.addressee_email).first()
        if not addressee:
            raise HTTPException(status_code=404, detail="User not found")
        if addressee.id == requester_id:
            raise HTTPException(status_code=400, detail="Cannot send request to yourself")

        existing = db.query(Friendship).filter(
            or_(
                and_(Friendship.requester_id == requester_id, Friendship.addressee_id == addressee.id),
                and_(Friendship.requester_id == addressee.id, Friendship.addressee_id == requester_id)
            )
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Friend relationship already exists (status: {existing.status})")

        friendship = Friendship(
            id=str(uuid.uuid4()),
            requester_id=requester_id,
            addressee_id=addressee.id,
            status="pending"
        )
        db.add(friendship)
        db.commit()
        db.refresh(friendship)
        return friendship

    def respond_to_request(self, db: Session, user_id: str, friendship_id: str, action: str) -> Friendship:
        """Accept or reject a friend request (action: 'accept' | 'reject' | 'block')."""
        friendship = db.query(Friendship).filter(
            Friendship.id == friendship_id,
            Friendship.addressee_id == user_id,
            Friendship.status == "pending"
        ).first()
        if not friendship:
            raise HTTPException(status_code=404, detail="Friend request not found")

        status_map = {"accept": "accepted", "reject": "rejected", "block": "blocked"}
        friendship.status = status_map.get(action, "rejected")
        db.commit()
        db.refresh(friendship)
        return friendship

    def get_friends(self, db: Session, user_id: str) -> List[dict]:
        """Get all accepted friends for a user."""
        friendships = db.query(Friendship).filter(
            or_(
                Friendship.requester_id == user_id,
                Friendship.addressee_id == user_id
            ),
            Friendship.status == "accepted"
        ).all()

        result = []
        for f in friendships:
            friend_id = f.addressee_id if f.requester_id == user_id else f.requester_id
            friend = db.query(User).filter(User.id == friend_id).first()
            if friend:
                result.append({
                    "id": friend.id,
                    "email": friend.email,
                    "full_name": friend.full_name,
                    "bio": friend.bio,
                    "friendship_id": f.id
                })
        return result

    def get_pending_requests(self, db: Session, user_id: str) -> List[dict]:
        """Get incoming pending friend requests."""
        friendships = db.query(Friendship).filter(
            Friendship.addressee_id == user_id,
            Friendship.status == "pending"
        ).all()

        result = []
        for f in friendships:
            requester = db.query(User).filter(User.id == f.requester_id).first()
            if requester:
                result.append({
                    "friendship_id": f.id,
                    "requester_id": f.requester_id,
                    "requester_email": requester.email,
                    "requester_name": requester.full_name,
                    "sent_at": f.created_at.isoformat() if f.created_at else None
                })
        return result

    def remove_friend(self, db: Session, user_id: str, friendship_id: str) -> None:
        """Remove a friend or delete a friendship."""
        friendship = db.query(Friendship).filter(
            Friendship.id == friendship_id,
            or_(Friendship.requester_id == user_id, Friendship.addressee_id == user_id)
        ).first()
        if not friendship:
            raise HTTPException(status_code=404, detail="Friendship not found")
        db.delete(friendship)
        db.commit()

    # ── Shared Challenges ───────────────────────────────────────────────────

    def create_challenge(self, db: Session, creator_id: str, challenge_in: ChallengeCreate) -> SharedChallenge:
        """Create a group challenge and auto-add creator + invited friends."""
        # Validate invited friends are actual friends
        friend_ids = challenge_in.friend_ids or []

        challenge = SharedChallenge(
            id=str(uuid.uuid4()),
            creator_id=creator_id,
            title=challenge_in.title,
            description=challenge_in.description,
            category=challenge_in.category,
            duration_days=str(challenge_in.duration_days),
            daily_target=challenge_in.daily_target,
            weekly_target=challenge_in.weekly_target,
            start_date=challenge_in.start_date or datetime.utcnow(),
            is_active=True
        )
        db.add(challenge)
        db.flush()

        # Add creator as participant
        db.add(ChallengeParticipant(
            id=str(uuid.uuid4()),
            challenge_id=challenge.id,
            user_id=creator_id,
            progress_percent="0",
            days_completed="0"
        ))

        # Add invited friends
        for fid in friend_ids:
            # Verify friendship
            is_friend = db.query(Friendship).filter(
                or_(
                    and_(Friendship.requester_id == creator_id, Friendship.addressee_id == fid),
                    and_(Friendship.requester_id == fid, Friendship.addressee_id == creator_id)
                ),
                Friendship.status == "accepted"
            ).first()
            if is_friend:
                db.add(ChallengeParticipant(
                    id=str(uuid.uuid4()),
                    challenge_id=challenge.id,
                    user_id=fid,
                    progress_percent="0",
                    days_completed="0"
                ))

        db.commit()
        db.refresh(challenge)
        return challenge

    def get_challenges(self, db: Session, user_id: str) -> List[dict]:
        """Get all challenges the user is participating in."""
        participations = db.query(ChallengeParticipant).filter(
            ChallengeParticipant.user_id == user_id,
            ChallengeParticipant.is_active == True
        ).all()

        result = []
        for p in participations:
            challenge = db.query(SharedChallenge).filter(SharedChallenge.id == p.challenge_id).first()
            if challenge:
                # Get all participants with names
                participants = db.query(ChallengeParticipant).filter(
                    ChallengeParticipant.challenge_id == challenge.id
                ).all()
                participant_data = []
                for cp in participants:
                    u = db.query(User).filter(User.id == cp.user_id).first()
                    if u:
                        participant_data.append({
                            "user_id": cp.user_id,
                            "name": u.full_name or u.email,
                            "progress_percent": cp.progress_percent,
                            "days_completed": cp.days_completed
                        })
                result.append({
                    "id": challenge.id,
                    "creator_id": challenge.creator_id,
                    "title": challenge.title,
                    "description": challenge.description,
                    "category": challenge.category,
                    "duration_days": challenge.duration_days,
                    "daily_target": challenge.daily_target,
                    "weekly_target": challenge.weekly_target,
                    "is_active": challenge.is_active,
                    "start_date": challenge.start_date.isoformat() if challenge.start_date else None,
                    "end_date": challenge.end_date.isoformat() if challenge.end_date else None,
                    "my_progress": p.progress_percent,
                    "participants": participant_data,
                    "created_at": challenge.created_at.isoformat()
                })
        return result

    def update_challenge_progress(
        self, db: Session, user_id: str, challenge_id: str, update: ChallengeProgressUpdate
    ) -> dict:
        """Update a participant's progress in a challenge."""
        participant = db.query(ChallengeParticipant).filter(
            ChallengeParticipant.challenge_id == challenge_id,
            ChallengeParticipant.user_id == user_id
        ).first()
        if not participant:
            raise HTTPException(status_code=404, detail="Not a participant in this challenge")

        participant.progress_percent = str(update.progress_percent)
        if update.days_completed is not None:
            participant.days_completed = str(update.days_completed)
        participant.last_check_in = datetime.utcnow()
        db.commit()
        return {"message": "Progress updated", "progress": update.progress_percent}

    # ── Encouragement Messages ──────────────────────────────────────────────

    def send_encouragement(self, db: Session, sender_id: str, msg_in: EncouragementCreate) -> EncouragementMessage:
        """Send an encouragement message to a friend."""
        # Verify friendship
        is_friend = db.query(Friendship).filter(
            or_(
                and_(Friendship.requester_id == sender_id, Friendship.addressee_id == msg_in.recipient_id),
                and_(Friendship.requester_id == msg_in.recipient_id, Friendship.addressee_id == sender_id)
            ),
            Friendship.status == "accepted"
        ).first()
        if not is_friend:
            raise HTTPException(status_code=403, detail="Can only send messages to friends")

        msg = EncouragementMessage(
            id=str(uuid.uuid4()),
            sender_id=sender_id,
            recipient_id=msg_in.recipient_id,
            challenge_id=msg_in.challenge_id,
            message=msg_in.message
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)
        return msg

    def get_messages(self, db: Session, user_id: str) -> List[dict]:
        """Get encouragement messages received by the user."""
        messages = db.query(EncouragementMessage).filter(
            EncouragementMessage.recipient_id == user_id
        ).order_by(EncouragementMessage.created_at.desc()).limit(50).all()

        result = []
        for m in messages:
            sender = db.query(User).filter(User.id == m.sender_id).first()
            result.append({
                "id": m.id,
                "sender_id": m.sender_id,
                "sender_name": sender.full_name or sender.email if sender else "Unknown",
                "recipient_id": m.recipient_id,
                "challenge_id": m.challenge_id,
                "message": m.message,
                "is_read": m.is_read,
                "created_at": m.created_at.isoformat()
            })
        return result

    def mark_message_read(self, db: Session, user_id: str, message_id: str) -> None:
        msg = db.query(EncouragementMessage).filter(
            EncouragementMessage.id == message_id,
            EncouragementMessage.recipient_id == user_id
        ).first()
        if msg:
            msg.is_read = True
            db.commit()

    # ── Focus Together ──────────────────────────────────────────────────────

    def _generate_session_code(self) -> str:
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    def create_focus_session(self, db: Session, host_id: str, session_in: FocusSessionCreate) -> FocusTogetherSession:
        code = self._generate_session_code()
        while db.query(FocusTogetherSession).filter(FocusTogetherSession.session_code == code).first():
            code = self._generate_session_code()

        session = FocusTogetherSession(
            id=str(uuid.uuid4()),
            host_id=host_id,
            title=session_in.title,
            duration_minutes=str(session_in.duration_minutes),
            status="waiting",
            session_code=code
        )
        db.add(session)
        db.flush()
        db.add(FocusSessionParticipant(
            id=str(uuid.uuid4()),
            session_id=session.id,
            user_id=host_id
        ))
        db.commit()
        db.refresh(session)
        return session

    def join_focus_session(self, db: Session, user_id: str, session_code: str) -> dict:
        session = db.query(FocusTogetherSession).filter(
            FocusTogetherSession.session_code == session_code,
            FocusTogetherSession.status.in_(["waiting", "active"])
        ).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or already ended")

        existing = db.query(FocusSessionParticipant).filter(
            FocusSessionParticipant.session_id == session.id,
            FocusSessionParticipant.user_id == user_id
        ).first()
        if not existing:
            db.add(FocusSessionParticipant(
                id=str(uuid.uuid4()),
                session_id=session.id,
                user_id=user_id
            ))
            db.commit()

        return {"message": "Joined session", "session_id": session.id, "code": session_code}

    def get_activity_feed(self, db: Session, user_id: str) -> List[dict]:
        """Public activity feed: friends' completed challenges/milestones."""
        friends = self.get_friends(db, user_id)
        friend_ids = [f["id"] for f in friends]

        feed = []
        for fid in friend_ids[:10]:  # limit to 10 friends
            friend = db.query(User).filter(User.id == fid).first()
            if not friend:
                continue
            # Get their completed challenge progress (public)
            completions = db.query(ChallengeParticipant).filter(
                ChallengeParticipant.user_id == fid,
                ChallengeParticipant.last_check_in != None
            ).order_by(ChallengeParticipant.last_check_in.desc()).limit(3).all()

            for cp in completions:
                challenge = db.query(SharedChallenge).filter(SharedChallenge.id == cp.challenge_id).first()
                if challenge:
                    feed.append({
                        "type": "challenge_progress",
                        "user_id": fid,
                        "user_name": friend.full_name or friend.email,
                        "challenge_title": challenge.title,
                        "progress": cp.progress_percent,
                        "timestamp": cp.last_check_in.isoformat() if cp.last_check_in else None
                    })

        feed.sort(key=lambda x: x.get("timestamp") or "", reverse=True)
        return feed[:20]


friend_service = FriendService()
