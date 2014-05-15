from flask import request, jsonify
from flask.ext.restful import Resource
from pydio.job.job_config import JobConfig
import json

class JobManager(Resource):

    config_file = ''
    jobs = None

    def get_jobs(self):
        if self.jobs:
            return self.jobs
        jobs = {}
        if not self.config_file:
            return jobs
        with open(self.config_file) as fp:
            data = json.load(fp, object_hook=JobConfig.object_decoder)
        if data:
            for j in data:
                jobs[j.uuid()] = j
            self.jobs = jobs
        return jobs

    def save_jobs(self, jobs):
        self.jobs = None
        all_jobs = []
        for k in jobs:
            all_jobs.append(JobConfig.encoder(jobs[k]))
        with open(self.config_file, "w") as fp:
            json.dump(all_jobs, fp, indent=2)

    def post(self):
        jobs = self.get_jobs()
        json_req = request.get_json()
        test_job = JobConfig.object_decoder(json_req)
        jobs[test_job.id] = test_job
        self.save_jobs(jobs)
        jobs = self.get_jobs()
        return JobConfig.encoder(test_job)

    def get(self, job_id = None):
        jobs = self.get_jobs()
        if not job_id:
            std_obj = []
            for k in jobs:
                std_obj.append(JobConfig.encoder(jobs[k]))
            return std_obj
        return JobConfig.encoder(jobs[job_id])

    def delete(self, job_id):
        jobs = self.get_jobs()
        del jobs[job_id]
        return job_id + "deleted", 204

    @classmethod
    def make_job_manager(cls, file):
        cls.config_file = file
        return cls

        #curl --data '{"__type__" : "JobConfig", "id" : 1, "server" : "http://localhost", "workspace" : "ws-watched", "directory" : "/Users/charles/Documents/SYNCTESTS/subfolder", "remote_folder" : "/test", "user" : "Administrator", "password" : "xxxxxx", "direction" : "bi", "active" : true}' http://localhost:5000/jobs  --header 'Content-Type: application/json' --header 'Accept: application/json'