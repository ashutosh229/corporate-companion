import os
import json
from langchain.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class FileCategories(BaseModel):
    """Model for file categorization results."""
    categories: Dict[str, str] = Field(description="Dictionary mapping filenames to categories")

class MeetingSlot(BaseModel):
    """Model for available meeting slots."""
    date: str = Field(description="Date of the meeting in YYYY-MM-DD format")
    start_time: str = Field(description="Start time in HH:MM format")
    end_time: str = Field(description="End time in HH:MM format")
    duration: float = Field(description="Duration of the meeting in hours")
    participants: List[str] = Field(description="List of meeting participants")

class HRPolicies(BaseModel):
    """Model for HR policy information."""
    title: str = Field(description="Title of the policy")
    description: str = Field(description="Description of the policy")
    details: Optional[str] = Field(description="Additional details or clarifications")

class LLMInterface:
    def __init__(self, model_path="models/llama-3-8b-instruct.Q4_K_M.gguf"):
        """Initialize the LLM interface with a local model."""
        # Set up directories
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # For real implementation, download or supply the model
        # Here we'll use a fallback to ensure the code runs
        try:
            # Initialize LlamaCpp model if available
            callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
            self.llm = LlamaCpp(
                model_path=model_path,
                temperature=0.1,
                max_tokens=2000,
                n_ctx=4096,
                callback_manager=callback_manager,
                verbose=False
            )
        except:
            # Fallback to a mock LLM for demo purposes
            self.llm = MockLLM()
    
    def categorize_files(self, files):
        """Categorize files using LLM."""
        # Define the prompt for file categorization
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
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        # Run the chain
        files_str = "\n".join(files)
        result = chain.run(files=files_str)
        
        try:
            # Parse the result
            output = parser.parse(result)
            return output.categories
        except Exception as e:
            print(f"Error parsing LLM output: {e}")
            
            # Fallback to basic categorization if parsing fails
            categories = {}
            for file in files:
                lower_file = file.lower()
                if any(term in lower_file for term in ["budget", "finance", "report", "tax", "expense", "balance"]):
                    categories[file] = "finance"
                elif any(term in lower_file for term in ["hr", "employee", "leave", "onboarding", "review", "benefit"]):
                    categories[file] = "hr"
                else:
                    categories[file] = "other"
            
            return categories
    
    def process_hr_query(self, query):
        """Process HR-related queries using LLM."""
        # Define HR policies (in a real system, these would be loaded from a database)
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
        
        # Define the prompt for HR queries
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
                "events": json.dumps(events, indent=2)
            }
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        # Run the chain
        try:
            result = chain.run(query=query)
            return result.strip()
        except Exception as e:
            print(f"Error processing HR query: {e}")
            return "I'm sorry, I couldn't process your query. Please try again with a different question about HR policies or company events."


class MockLLM:
    """Mock LLM class for demonstration purposes."""
    def __call__(self, prompt, *args, **kwargs):
        """Simple implementation for demonstration."""
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