from django.db import models
import json


class TemporaryTable(models.Model):
    json_data = models.TextField()
    file_name = models.TextField()

    class Meta:
        app_label = "app"

    def create_from_json(json_data, file_name):
        # before adding any file data we delete the previous data
        TemporaryTable.delete_json_data()
        table = TemporaryTable(json_data=json.dumps(json_data), file_name=file_name)
        table.save()

    def get_file_name():
        your_model = TemporaryTable.objects.first()
        if your_model:
            return (your_model.file_name,)

        return None

    def get_json_data():
        your_model = TemporaryTable.objects.first()
        if your_model:
            return json.loads(your_model.json_data)

        return None

    def delete_json_data():
        record = TemporaryTable.objects.first()
        if record:
            # Delete the record
            record.delete()
            print("Record deleted successfully.")
        else:
            print("Record not found.")
