
import datetime
import threading
import requests
from src.models import Build, Workflow


class CiData():
    def __init__(self, github_token, db):
        self.docker_api_url = "https://hub.docker.com/v2/namespaces/elblogbruno/repositories/hvac-log680-eq12/tags"
        self.github = "https://api.github.com/repos/damiendesvent/hvac_LOG680-01_H2023_EQ12/actions/runs?per_page=90"
        self.github_token = github_token
        
        self.db = db 
        self.old_data = []

    def start(self):
        threading.Thread(target=self.update).start()
        
    def update(self):
        self.update_ci_on_database()

        # sleep for 1 minute before updating again
        threading.Timer(60, self.update).start()



    def _get_docker_data(self):

        """
        Add this headers to a request to the docker api to avoid CORS issues

        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,PUT,PATCH,POST,DELETE",
        "Access-Control-Allow-Headers":
            "Origin, X-Requested-With, Content-Type, Accept",

        """

        print("Getting docker data")
        print(self.docker_api_url)

        response = requests.get(self.docker_api_url, headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,PUT,PATCH,POST,DELETE",
            "Access-Control-Allow-Headers":
                "Origin, X-Requested-With, Content-Type, Accept",
        })
        
        return response
    
    def _get_github_data(self):
        response = requests.get(self.github, headers={
            "Authorization": f"Bearer {self.github_token}",
        })
        
        return response.json()
    
    def _calculate_build_time(self, github_data, image_name):
        # order by created_at
        github_data = sorted(github_data, key=lambda k: k['created_at'])
        
        workflow_recent = github_data[-1]

        if image_name == 'latest':
            # get most recent workflow
            created_at = datetime.datetime.strptime(workflow_recent['created_at'], "%Y-%m-%dT%H:%M:%SZ")
            updated_at = datetime.datetime.strptime(workflow_recent['updated_at'], "%Y-%m-%dT%H:%M:%SZ")

            return (updated_at - created_at).total_seconds()

        for workflow in github_data:
            if workflow['head_sha'] == image_name:
                # get created_at and updated_at and calculate the difference
                created_at = datetime.datetime.strptime(workflow['created_at'], "%Y-%m-%dT%H:%M:%SZ")
                updated_at = datetime.datetime.strptime(workflow['updated_at'], "%Y-%m-%dT%H:%M:%SZ")
                return (updated_at - created_at).total_seconds()
            
        return 0
    
    def update_ci_on_database(self):
        print("Updating ci data")
        try:
            data = self._get_docker_data()

            data = data.json()['results']
            
            github_data = self._get_github_data()['workflow_runs']

            

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
                            build_time = self._calculate_build_time(github_data, element["name"]),
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
        except Exception as e:
            print(e)
            return
        