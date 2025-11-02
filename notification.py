import asyncio
import os
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

from metorial import Metorial
from openai import AsyncOpenAI

async def add_to_calendar(datetime: datetime):
  try:
    # Initialize clients
    metorial_api_key = os.getenv("METORIAL_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    google_cal_deployment_id = os.getenv("GOOGLE_CALENDAR_DEPLOYMENT_ID")

    # Validate environment variables
    if not metorial_api_key:
      print("❌ Error: METORIAL_API_KEY not found in .env file")
      return
    if not openai_api_key:
      print("❌ Error: OPENAI_API_KEY not found in .env file")
      return
    if not google_cal_deployment_id:
      print("❌ Error: GOOGLE_CALENDAR_DEPLOYMENT_ID not found in .env file")
      return

    print("✓ Environment variables loaded successfully")
    print(f"   METORIAL_API_KEY: {metorial_api_key[:20]}...")
    print(f"   OPENAI_API_KEY: {openai_api_key[:20]}...")
    print(f"   GOOGLE_CALENDAR_DEPLOYMENT_ID: {google_cal_deployment_id}")

    metorial = Metorial(api_key=metorial_api_key)
    openai = AsyncOpenAI(api_key=openai_api_key)

    print(f"\n🔗 Creating OAuth session for deployment: {google_cal_deployment_id}")

    try:
      oauth_session = metorial.oauth.sessions.create(
        server_deployment_id=google_cal_deployment_id
      )
      print(f"✅ OAuth session created successfully!")
      print(f"   Session ID: {oauth_session.id}")
      print(f"   Session URL: {oauth_session.url}")
    except Exception as e:
      print(f"❌ Failed to create OAuth session: {str(e)}")
      print(f"   Error type: {type(e).__name__}")
      return

    print("\n⏳ Waiting for OAuth completion...")
    print("   Please open the URL above and authorize access")

    try:
      await asyncio.wait_for(
        metorial.oauth.wait_for_completion([oauth_session]),
        timeout=300.0  # 5 minute timeout
      )
      print("✅ OAuth session completed!")
    except asyncio.TimeoutError:
      print("❌ OAuth completion timeout (5 minutes). Please try again.")
      return
    except Exception as e:
      print(f"❌ OAuth completion failed: {str(e)}")
      print(f"   Error type: {type(e).__name__}")
      return

    print("\n📅 Creating calendar event...")
    print(f"   Date: {datetime.date()}")
    print(f"   Time: {datetime.time()}")

    try:
      result = await metorial.run(
        message=f"""Create a Google Calendar event with the following details:
- Title: "Model Training Scheduled"
- Date: {datetime.date()}
- Time: {datetime.time()}
- Guest email: aishwaryagune@gmail.com
- Description: "GPU training job scheduled via GPU Finder platform"

Please create this event and confirm it was created successfully.""",
        server_deployments=[
          { "serverDeploymentId": google_cal_deployment_id, "oauthSessionId": oauth_session.id },
        ],
        client=openai,
        model="gpt-4o",
        max_tokens=4096,
        max_steps=25,
      )

      print("\n✅ Calendar event created successfully!")
      print(f"📋 Result: {result.text}")

    except Exception as e:
      print(f"❌ Failed to create calendar event: {str(e)}")
      print(f"   Error type: {type(e).__name__}")
      import traceback
      traceback.print_exc()
      return

  except Exception as e:
    print(f"❌ Unexpected error: {str(e)}")
    print(f"   Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()

if __name__ == "__main__":
  asyncio.run(add_to_calendar(datetime=datetime(2025, 11, 2, 10, 0, 0)))