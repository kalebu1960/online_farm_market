import argparse
import os
from .db import SessionLocal, engine
from .models import User, Category, Item, Photo, Base
from .utils import hash_password, verify_password, save_session, load_session, clear_session
from .seed import init_db as seed_init_db

def init_db():
    Base.metadata.create_all(bind=engine)
    seed_init_db()
    print("Database initialized and categories seeded.")

def register(args):
    db = SessionLocal()
    existing = db.query(User).filter(User.email == args.email).first()
    if existing:
        print("Email already registered.")
        db.close()
        return
    hashed = hash_password(args.password)
    user = User(name=args.name, email=args.email, password_hash=hashed, phone=args.phone)
    db.add(user)
    db.commit()
    db.close()
    print("Registered successfully.")

def login(args):
    db = SessionLocal()
    user = db.query(User).filter(User.email == args.email).first()
    if not user:
        print("No account with that email.")
        db.close()
        return
    if not verify_password(args.password, user.password_hash):
        print("Invalid credentials.")
        db.close()
        return
    save_session({"user_id": user.id, "email": user.email})
    db.close()
    print(f"Logged in as {user.email}.")

def logout(args):
    clear_session()
    print("Logged out.")

def add_item(args):
    sess = load_session()
    if not sess:
        print("Please login first.")
        return
    if not args.photo1 or not args.photo2:
        print("Two photos are required (--photo1 and --photo2).")
        return
    db = SessionLocal()
    seller = db.query(User).filter(User.id == sess["user_id"]).first()
    if not seller:
        print("Logged-in user not found.")
        db.close()
        return
    cat = db.query(Category).filter(Category.name == args.category).first()
    if not cat:
        print("Category not found. Use 'list-categories' to see available categories.")
        db.close()
        return
    item = Item(title=args.title, description=args.description or "", price=args.price, seller=seller, category=cat)
    db.add(item)
    db.commit()
    # save photos
    p1 = Photo(path=args.photo1, item=item)
    p2 = Photo(path=args.photo2, item=item)
    db.add_all([p1, p2])
    db.commit()
    print(f"Item added with id {item.id}.")
    db.close()

def list_categories(args):
    db = SessionLocal()
    cats = db.query(Category).all()
    for c in cats:
        print(f"- {c.name}")
    db.close()

def list_items(args):
    db = SessionLocal()
    query = db.query(Item)
    if args.category:
        query = query.join(Category).filter(Category.name == args.category)
    items = query.all()
    if not items:
        print("No items found.")
        db.close()
        return
    for it in items:
        seller_phone = it.seller.phone if it.seller else "-"
        print(f"[{it.id}] {it.title} | KES {it.price} | Seller: {it.seller.email} | Phone: {seller_phone} | Category: {it.category.name}")
    db.close()

def view_item(args):
    db = SessionLocal()
    it = db.query(Item).filter(Item.id == args.id).first()
    if not it:
        print("Item not found.")
        db.close()
        return
    print(f"ID: {it.id}")
    print(f"Title: {it.title}")
    print(f"Description: {it.description}")
    print(f"Price: KES {it.price}")
    print(f"Seller: {it.seller.name} ({it.seller.email})")
    print(f"Phone: {it.seller.phone}")
    print(f"Category: {it.category.name}")
    print("Photos:")
    for p in it.photos:
        print(f"- {p.path}")
    db.close()

def build_parser():
    p = argparse.ArgumentParser(prog="online_farm_market")
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("init-db")
    sp.set_defaults(func=lambda a: init_db())

    sp = sub.add_parser("register")
    sp.add_argument("--name", required=True)
    sp.add_argument("--email", required=True)
    sp.add_argument("--password", required=True)
    sp.add_argument("--phone", required=True)
    sp.set_defaults(func=register)

    sp = sub.add_parser("login")
    sp.add_argument("--email", required=True)
    sp.add_argument("--password", required=True)
    sp.set_defaults(func=login)

    sp = sub.add_parser("logout")
    sp.set_defaults(func=logout)

    sp = sub.add_parser("add-item")
    sp.add_argument("--title", required=True)
    sp.add_argument("--description")
    sp.add_argument("--price", type=float, required=True)
    sp.add_argument("--category", required=True)
    sp.add_argument("--photo1", required=True)
    sp.add_argument("--photo2", required=True)
    sp.set_defaults(func=add_item)

    sp = sub.add_parser("list-categories")
    sp.set_defaults(func=list_categories)

    sp = sub.add_parser("list-items")
    sp.add_argument("--category")
    sp.set_defaults(func=list_items)

    sp = sub.add_parser("view-item")
    sp.add_argument("--id", type=int, required=True)
    sp.set_defaults(func=view_item)

    return p

def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
