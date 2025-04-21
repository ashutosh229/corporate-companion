import json
from typing import Dict, List, Optional
from langchain_community.llms.huggingface_hub import HuggingFaceHub
from langchain_core.language_models.llms import LLM
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class FileCategories(BaseModel):
    categories: Dict[str, str] = Field(
        ..., description="Dictionary mapping filenames to categories"
    )
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "categories": {
                        "expense_report_march.pdf": "Finance",
                        "tax_documentation.pdf": "Finance",
                        "employee_policy.docx": "HR",
                    }
                }
            ]
        }
    }


class MeetingSlot(BaseModel):
    date: str = Field(description="Date of the meeting in YYYY-MM-DD format")
    start_time: str = Field(description="Start time in HH:MM format")
    end_time: str = Field(description="End time in HH:MM format")
    duration: float = Field(description="Duration of the meeting in hours")
    participants: List[str] = Field(description="List of meeting participants")


class HRPolicies(BaseModel):
    title: str = Field(description="Title of the policy")
    description: str = Field(description="Description of the policy")
    details: Optional[str] = Field(description="Additional details or clarifications")


class MockLLM(LLM):
    @property
    def _llm_type(self) -> str:
        return "mock_llm"

    def _call(
        self,
        prompt: str,
    ) -> str:
        if "categorize" in prompt.lower() and "files" in prompt.lower():
            return """
            {
                "categories": {
                    "quarterly_report_Q1.pdf": "Finance",
                    "balance_sheet.xlsx": "Finance",
                    "annual_budget_2025.xlsx": "Finance",
                    "expense_report_march.pdf": "Finance",
                    "tax_documentation.pdf": "Finance",
                    "employee_policy.docx": "HR",
                    "leave_form.pdf": "HR",
                    "onboarding_checklist.docx": "HR",
                    "performance_review_template.docx": "HR",
                    "benefits_overview.pdf": "HR"
                }
            }
            """
        elif "HR" in prompt and "query" in prompt:
            return "Based on our company policies, employees are entitled to 20 days of paid leave annually. These days are accrued on a monthly basis. For more details, please consult the employee handbook or contact the HR department directly."
        else:
            return "I've processed your request, here's my response."


class LLMInterface:
    def __init__(self, repo_id, task, model_kwargs, hugging_face_token):
        try:
            self.llm = HuggingFaceHub(
                repo_id=repo_id,
                model_kwargs=model_kwargs,
                huggingfacehub_api_token=hugging_face_token,
                verbose=False,
                task=task,
            )
            print("Real llm initialized")
        except Exception as e:
            print(f"Error initializing LlamaCpp: {e}")
            self.llm = MockLLM()
            print("mock llm initialized")

    def categorize_files(self, files):
        template = """
        You are an expert file organizer. Your task is to categorize the following files into logical groups.
        
        Files:
        {files}
        
        Categorize each file into one of these categories: Finance or HR.
        Return your answer as a JSON object where the keys are the filenames and the values are the categories.
        
        {format_instructions}
        """

        parser = PydanticOutputParser(pydantic_object=FileCategories)

        prompt = PromptTemplate(
            template=template,
            input_variables=["files"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        chain = LLMChain(llm=self.llm, prompt=prompt)

        files_str = "\n".join(files)
        try:
            result = chain.run(files=files_str)
            parsed_output = parser.parse(result)
            print("Real chain ran")
            return parsed_output.categories
        except Exception as e:
            print(f"Error parsing LLM output: {e}")

            categories = {}
            for file in files:
                lower_file = file.lower()
                if any(
                    term in lower_file
                    for term in [
                        "budget",
                        "finance",
                        "report",
                        "tax",
                        "expense",
                        "balance",
                    ]
                ):
                    categories[file] = "finance"
                elif any(
                    term in lower_file
                    for term in [
                        "hr",
                        "employee",
                        "leave",
                        "onboarding",
                        "review",
                        "benefit",
                    ]
                ):
                    categories[file] = "hr"
                else:
                    categories[file] = "other"

            return categories

    def process_hr_query(self, query):
        hr_policies = {
            "leave": "Employees are entitled to 20 days of paid leave annually, accrued monthly.",
            "remote_work": "Remote work is available for eligible employees up to 2 days per week.",
            "benefits": "The company offers health insurance, 401(k), and professional development benefits.",
            "holidays": "The company observes 10 federal holidays and provides 2 floating holidays.",
            "dress_code": "Business casual attire is required in the office.",
        }

        events = {
            "company_picnic": "Annual company picnic on June 15, 2025 at Central Park.",
            "quarterly_review": "Q2 review meetings scheduled for July 1-5, 2025.",
            "training": "Mandatory security training on April 25, 2025.",
            "team_building": "Department team building events scheduled for May 10-15, 2025.",
        }

        template = """
        You are a knowledgeable HR assistant. Answer the following query based on company policies and upcoming events.
        
        Query: {query}
        
        HR Policies:
        {policies}
        
        Upcoming Events:
        {events}
        
        Remember to be professional, helpful, and concise in your response.
        """

        prompt = PromptTemplate(
            template=template,
            input_variables=["query"],
            partial_variables={
                "policies": json.dumps(hr_policies, indent=2),
                "events": json.dumps(events, indent=2),
            },
        )

        chain = LLMChain(llm=self.llm, prompt=prompt)

        try:
            result = chain.run(query=query)
            return result.strip()
        except Exception as e:
            print(f"Error processing HR query: {e}")
            return "I'm sorry, I couldn't process your query. Please try again with a different question about HR policies or company events."
