# from django_elasticsearch_dsl import Document
# from django_elasticsearch_dsl.registries import registry
# from .models import User
#
# @registry.register_document
# class UserDocument(Document):
#     class Index:
#         # Specify the Elasticsearch index name
#         name = 'userdata'
#
#     class Django:
#         # Associate the document with the Django User model
#         model = User
#         fields = [
#             'username',
#             'first_name',
#             'last_name',
#             'email',
#             # Add any additional fields you need to index
#         ]
