# test_api.py (idempotent version)
import os
import sys
import json
import traceback

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

import django
from django.core.management import call_command
from django.test import Client
django.setup()

from django.contrib.auth.models import User
from api.models import Movie, Show, Booking

def safe_print_json(resp):
    try:
        print(json.dumps(resp, indent=2))
    except Exception:
        print(resp)

def cleanup_test_data():
    # Remove test user if exists
    try:
        u = User.objects.filter(username='testuser')
        if u.exists():
            print("Cleaning up existing test user 'testuser' and related bookings...")
            # delete bookings for that user (if any)
            Booking.objects.filter(user__username='testuser').delete()
            u.delete()
    except Exception as e:
        print("Cleanup user error:", e)

    # Remove any leftover bookings on seat 5 for any show used in tests
    try:
        Booking.objects.filter(seat_number=5).delete()
    except Exception as e:
        print("Cleanup booking error:", e)

def main():
    overall_ok = True
    try:
        print("\n1) Running migrations...")
        call_command("makemigrations", interactive=False)
        call_command("migrate", interactive=False)
        print("  -> migrations done")

        # Seed DB (if seed_script.py exists)
        seed_path = os.path.join(BASE_DIR, "seed_script.py")
        if os.path.exists(seed_path):
            print("\n2) Executing seed_script.py ...")
            with open(seed_path, "r", encoding="utf-8") as f:
                code = f.read()
            exec(code, {"__name__": "__main__"})
            print("  -> seed done")
        else:
            print("  -> seed_script.py not found; skipping seed (ok if you don't have it)")

        # Cleanup leftover test data to ensure idempotent runs
        cleanup_test_data()

        client = Client()

        print("\n3) Testing Signup endpoint: POST /api/signup/")
        signup_resp = client.post(
            "/api/signup/",
            data=json.dumps({"username": "testuser", "password": "pass1234"}),
            content_type="application/json",
        )
        print("  status:", signup_resp.status_code)
        try:
            print("  response:")
            safe_print_json(signup_resp.json())
        except:
            print("  (no json response)")

        if signup_resp.status_code not in (200, 201):
            # If username existed, attempt to continue by logging in
            print("  -> SIGNUP returned non-201. Attempting to continue (maybe user already exists).")
            overall_ok = overall_ok and (signup_resp.status_code in (200,201))
        else:
            print("  -> SIGNUP OK")

        print("\n4) Testing Login endpoint: POST /api/login/")
        login_resp = client.post(
            "/api/login/",
            data=json.dumps({"username": "testuser", "password": "pass1234"}),
            content_type="application/json",
        )
        print("  status:", login_resp.status_code)
        try:
            login_json = login_resp.json()
            safe_print_json(login_json)
        except Exception:
            login_json = {}
            print("  -> could not parse JSON from login response")
            overall_ok = False

        access = login_json.get("access")
        if not access:
            print("  -> LOGIN FAILED (no access token). Test cannot continue.")
            overall_ok = False
            print("\nFINAL: Overall result:", "PASS" if overall_ok else "FAIL")
            return

        print("  -> LOGIN OK (access token received)")

        auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {access}"}

        print("\n5) Testing GET /api/movies/")
        movies_resp = client.get("/api/movies/")
        print("  status:", movies_resp.status_code)
        try:
            movies = movies_resp.json()
            safe_print_json(movies)
        except Exception:
            movies = []
            print("  -> could not parse movies response (expected JSON)")
            overall_ok = False

        if movies_resp.status_code != 200:
            print("  -> GET /api/movies failed")
            overall_ok = False
        else:
            print("  -> GET /api/movies OK")

        movie_id = None
        if isinstance(movies, list) and len(movies) > 0:
            movie_id = movies[0].get("id")
        else:
            movie_id = 1

        print(f"\n6) Testing GET /api/movies/{movie_id}/shows/")
        shows_resp = client.get(f"/api/movies/{movie_id}/shows/")
        print("  status:", shows_resp.status_code)
        try:
            shows = shows_resp.json()
            safe_print_json(shows)
        except Exception:
            shows = []
            print("  -> could not parse shows response")
            overall_ok = False

        if shows_resp.status_code != 200:
            print("  -> GET shows failed")
            overall_ok = False
        else:
            print("  -> GET shows OK")

        show_id = None
        if isinstance(shows, list) and len(shows) > 0:
            first = shows[0]
            show_id = first.get("id") if isinstance(first, dict) else None
        else:
            show_id = 1

        # Ensure no leftover bookings for this show+seat
        try:
            Booking.objects.filter(show_id=show_id, seat_number=5).delete()
            print(f"  -> Cleaned any existing bookings for show {show_id}, seat 5")
        except Exception as e:
            print("  -> error cleaning bookings:", e)

        print(f"\n7) Testing booking flow on show id {show_id}")

        print("7.a) Book seat 5 (first attempt) -> expect success")
        book_resp = client.post(
            f"/api/shows/{show_id}/book/",
            data=json.dumps({"seat_number": 5}),
            content_type="application/json",
            **auth_headers,
        )
        print("  status:", book_resp.status_code)
        try:
            bjson = book_resp.json()
            safe_print_json(bjson)
        except Exception:
            bjson = {}
            print("  -> could not parse booking response")
            overall_ok = False

        if book_resp.status_code not in (200, 201):
            print("  -> BOOKING FAILED (first attempt).")
            overall_ok = False
        else:
            print("  -> BOOKING OK (first attempt)")

        booking_id = bjson.get("id") or bjson.get("pk") or None
        if not booking_id:
            print("  -> booking id not returned, fetching /api/my-bookings/")
            myb_resp = client.get("/api/my-bookings/", **auth_headers)
            print("   my-bookings status:", myb_resp.status_code)
            try:
                mb = myb_resp.json()
                safe_print_json(mb)
                if isinstance(mb, list) and len(mb) > 0:
                    booking_id = mb[0].get("id") or mb[0].get("pk")
            except Exception:
                print("   -> could not parse my bookings")
                overall_ok = False

        if not booking_id:
            print("  -> Could not determine booking id. Further tests may fail.")
            overall_ok = False

        print("7.b) Attempt double booking same seat number (expect failure)")
        book2_resp = client.post(
            f"/api/shows/{show_id}/book/",
            data=json.dumps({"seat_number": 5}),
            content_type="application/json",
            **auth_headers,
        )
        print("  status:", book2_resp.status_code)
        try:
            safe_print_json(book2_resp.json())
        except:
            pass

        if book2_resp.status_code in (200, 201):
            print("  -> DOUBLE BOOKING ALLOWED (FAIL). Should not happen.")
            overall_ok = False
        else:
            print("  -> DOUBLE BOOKING prevented (OK)")

        print("\n8) GET /api/my-bookings/")
        myb_resp = client.get("/api/my-bookings/", **auth_headers)
        print("  status:", myb_resp.status_code)
        try:
            safe_print_json(myb_resp.json())
        except:
            print("  -> could not parse response")
            overall_ok = False

        if myb_resp.status_code != 200:
            overall_ok = False
        else:
            print("  -> my-bookings OK")

        if booking_id:
            print(f"\n9) Cancel booking id {booking_id} -> POST /api/bookings/{booking_id}/cancel/")
            cancel_resp = client.post(f"/api/bookings/{booking_id}/cancel/", **auth_headers)
            print("  status:", cancel_resp.status_code)
            try:
                safe_print_json(cancel_resp.json())
            except:
                pass

            if cancel_resp.status_code not in (200, 201):
                print("  -> CANCEL booking failed")
                overall_ok = False
            else:
                print("  -> CANCEL booking OK")

            print("9.b) After cancel, try booking same seat again (expect success)")
            book3_resp = client.post(
                f"/api/shows/{show_id}/book/",
                data=json.dumps({"seat_number": 5}),
                content_type="application/json",
                **auth_headers,
            )
            print("  status:", book3_resp.status_code)
            try:
                safe_print_json(book3_resp.json())
            except:
                pass

            if book3_resp.status_code not in (200, 201):
                print("  -> Re-book after cancel failed (this means cancel didn't free seat).")
                overall_ok = False
            else:
                print("  -> Re-book after cancel OK (seat was freed)")

        else:
            print("  -> No booking id to cancel; skipping cancel tests")
            overall_ok = False

    except Exception as exc:
        print("\nERROR during test run:")
        traceback.print_exc()
        overall_ok = False

    print("\nFINAL: Overall result:", "PASS" if overall_ok else "FAIL")
    if not overall_ok:
        print("If tests failed, paste the output here and I will help debug.")

if __name__ == "__main__":
    main()
