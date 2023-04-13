
import datetime
import requests
from src.models import Build, Workflow

class CiData():
    def __init__(self, github_token, db):
        self.docker_api_url = "https://hub.docker.com/v2/namespaces/elblogbruno/repositories/hvac-log680-eq12/tags"
        self.github = "https://api.github.com/repos/damiendesvent/hvac_LOG680-01_H2023_EQ12/actions/runs?per_page=90"
        self.github_token = github_token
        
        self.db = db 
        self.old_data = []


    def _get_docker_data(self):

        """
        Add this headers to a request to the docker api to avoid CORS issues

        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,PUT,PATCH,POST,DELETE",
        "Access-Control-Allow-Headers":
            "Origin, X-Requested-With, Content-Type, Accept",

        """

        response = requests.get(self.docker_api_url, headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,PUT,PATCH,POST,DELETE",
            "Access-Control-Allow-Headers":
                "Origin, X-Requested-With, Content-Type, Accept",
        })
        
        return response.json()
    
    def _get_github_data(self):
        response = requests.get(self.github, headers={
            "Authorization": f"Bearer {self.github_token}",
        })
        
        return response.json()
    
    def update_ci_on_database(self):
        data = self._get_docker_data()['results']
        
        github_data = self._get_github_data()['workflow_runs']

        print(len(data), len(self.old_data))

        if len(data) != len(self.old_data) or data != self.old_data:
            print("Update CI")
            # get elements that are in data but not in self.old_data
            for element in data:
                if element not in self.old_data:
                    date = datetime.datetime.strptime(element["last_updated"], "%Y-%m-%dT%H:%M:%S.%fZ")
                    date = date.strftime("%Y-%m-%d %H:%M:%S")

                    build = Build(
                        name = element["name"],
                        version = element["name"],
                        size = element["full_size"],
                        date = str(date),
                    )

                    build.save(self.db)

        self.old_data = data

        workflow_dict = {}

        print(len(github_data))

        for workflow in github_data:
            if workflow['name'] not in workflow_dict:
                workflow_dict[workflow['name']] = {
                    'success': 0,
                    'failure': 0,
                }

                if workflow['conclusion'] == 'failure':
                    workflow_dict[workflow['name']]['failure'] += 1
                else:
                    workflow_dict[workflow['name']]['success'] += 1
                
            if workflow['conclusion'] == 'failure':
                workflow_dict[workflow['name']]['failure'] += 1
            else:
                workflow_dict[workflow['name']]['success'] += 1

        print(workflow_dict)

        for workflow in workflow_dict:
            workflow = Workflow(
                name = workflow,
                number_of_runs = workflow_dict[workflow]['success'] + workflow_dict[workflow]['failure'],
                number_of_success = workflow_dict[workflow]['success'],
                number_of_failures = workflow_dict[workflow]['failure'],
            )

            workflow.save(self.db)

        