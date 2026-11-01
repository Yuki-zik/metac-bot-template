"""Offline dry run: forecast a locally-built binary question with the configured LLM. Never publishes."""
import asyncio, os, sys
from datetime import datetime, timedelta
from forecasting_tools import BinaryQuestion, GeneralLlm
sys.argv=[sys.argv[0]]
import main
llm=lambda t: GeneralLlm(model="openai/"+os.environ["LLM_MODEL"], api_base=os.environ["LLM_BASE_URL"],
                        api_key=os.environ["LLM_API_KEY"], temperature=t, timeout=180, allowed_tries=2)
bot=main.FallTemplateBot2026(research_reports_per_question=1, predictions_per_research_report=1,
    publish_reports_to_metaculus=False, skip_previously_forecasted_questions=False,
    llms={"default":llm(0.3),"summarizer":llm(0),"researcher":llm(0),"parser":llm(0)})
q=BinaryQuestion(question_text="Will the US Federal Reserve cut rates at its December 2026 meeting?",
    id_of_post=0, id_of_question=0, page_url="https://example.invalid/q",
    background_info="Offline test question.", resolution_criteria="Resolves YES if the FOMC lowers the target range in Dec 2026.",
    fine_print="", scheduled_resolution_time=datetime.now()+timedelta(days=60))
r=asyncio.run(bot.forecast_question(q))
print("=== DRY RUN OK, prediction:", r.prediction, "(not submitted)")
