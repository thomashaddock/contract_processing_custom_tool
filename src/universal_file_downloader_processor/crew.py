import os

from crewai import LLM
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import (
	# VisionTool,
	PDFSearchTool
)
from .tools.custom_tool import PDFDownloadTool




@CrewBase
class UniversalFileDownloaderProcessorCrew:
    """UniversalFileDownloaderProcessor crew"""

    @agent
    def document_processor(self) -> Agent:
        embedding_config_pdfsearchtool = dict(
            llm=dict(
                provider="openai",
                config=dict(
                    model="gpt-4.1-mini",
                ),
            ),
            embedder=dict(
                provider="openai",
                config=dict(
                    model="text-embedding-3-large",
                ),
            ),
        )
        
        return Agent(
            config=self.agents_config["document_processor"],
            tools=[
				# VisionTool(),
				PDFSearchTool(config=embedding_config_pdfsearchtool),
				PDFDownloadTool()
            ],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=LLM(
                model="gpt-4.1-mini",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def contract_analyzer(self) -> Agent:

        return Agent(
            config=self.agents_config["contract_analyzer"],
            tools=[

            ],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=LLM(
                model="gpt-4.1-mini",
                temperature=0.7,
            ),
            
        )
    
    @agent
    def json_export_specialist(self) -> Agent:

        return Agent(
            config=self.agents_config["json_export_specialist"],
            tools=[

            ],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=LLM(
                model="gpt-4.1-mini",
                temperature=0.7,
            ),
            
        )
    

    
    @task
    def process_document_from_google_drive(self) -> Task:
        return Task(
            config=self.tasks_config["process_document_from_google_drive"],
            markdown=False,
        )
    
    @task
    def extract_contract_fields(self) -> Task:
        return Task(
            config=self.tasks_config["extract_contract_fields"],
            markdown=False,
        )
    
    @task
    def generate_json_export(self) -> Task:
        return Task(
            config=self.tasks_config["generate_json_export"],
            markdown=False,
        )
    

    @crew
    def crew(self) -> Crew:
        """Creates the UniversalFileDownloaderProcessor crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            tracing=True,
        )

    def _load_response_format(self, name):
        with open(os.path.join(self.base_directory, "config", f"{name}.json")) as f:
            json_schema = json.loads(f.read())

        return SchemaConverter.build(json_schema)
