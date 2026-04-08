from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class CrewAzam():
    """CrewAzam crew"""

    agents: list[BaseAgent]
    tasks: list[Task]
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def emailer(self) -> Agent:
        return Agent(
            config=self.agents_config['emailer'], # type: ignore[index]
            verbose=True
        )

    @agent
    def invoice_reader(self) -> Agent:
        return Agent(
            config=self.agents_config['invoice_reader'], # type: ignore[index]
            verbose=True
        )

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'], # type: ignore[index]
            verbose=True
        )

    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['reporting_analyst'], # type: ignore[index]
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def receive_email_task(self) -> Task:
        return Task(
            config=self.tasks_config['receive_email_task'], # type: ignore[index]
        )

    @task
    def convert_invoice_into_json_task(self) -> Task:
        return Task(
            config=self.tasks_config['convert_invoice_into_json_task'], # type: ignore[index]
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'], # type: ignore[index]
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'], # type: ignore[index]
            output_file='report.md'
        )

    def email_crew(self) -> Crew:
        """Creates a single-task crew for email processing."""
        return Crew(
            agents=[self.emailer()],
            tasks=[self.receive_email_task()],
            process=Process.sequential,
            verbose=True,
        )

    def invoice_crew(self) -> Crew:
        """Creates a single-task crew for invoice extraction."""
        return Crew(
            agents=[self.invoice_reader()],
            tasks=[self.convert_invoice_into_json_task()],
            process=Process.sequential,
            verbose=True,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the CrewAzam crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=[
                self.researcher(),
                self.reporting_analyst(),
            ],
            tasks=[
                self.research_task(),
                self.reporting_task(),
            ],
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
