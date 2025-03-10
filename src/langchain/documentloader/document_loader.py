import os
from langchain_community.document_loaders import (
    CSVLoader,
    TextLoader,
    PyPDFLoader,
    JSONLoader,
    UnstructuredMarkdownLoader,
    UnstructuredWordDocumentLoader,
    MongodbLoader,
    GithubFileLoader,
    BigQueryLoader,
    WebBaseLoader
)

class DocumentLoader:
    loader_map = {
        '.csv': CSVLoader,
        '.txt': TextLoader,
        '.md': UnstructuredMarkdownLoader,
        '.docx': UnstructuredWordDocumentLoader,
        '.pdf': PyPDFLoader,
        '.json': JSONLoader,
    }

    def __init__(self, file_path=None, jq_schema='.', json_text_content=True,
                 mongo_uri=None, db_name=None, collection_name=None, mongo_query=None,
                 github_repo=None, github_filepath=None, github_branch="main",
                 bigquery_project=None, bigquery_dataset=None, bigquery_table=None,
                 web_url=None):
        self.file_path = file_path
        self.jq_schema = jq_schema
        self.json_text_content = json_text_content
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.collection_name = collection_name
        self.mongo_query = mongo_query
        self.github_repo = github_repo
        self.github_filepath = github_filepath
        self.github_branch = github_branch
        self.bigquery_project = bigquery_project
        self.bigquery_dataset = bigquery_dataset
        self.bigquery_table = bigquery_table
        self.web_url = web_url

    def load(self):
        if self.mongo_uri and self.db_name and self.collection_name:
            loader = MongodbLoader(
                connection_string=self.mongo_uri,
                db_name=self.db_name,
                collection_name=self.collection_name,
                query=self.mongo_query
            )
            return loader.load()

        if self.github_repo and self.github_filepath:
            loader = GithubFileLoader(
                repo=self.github_repo,
                file_path=self.github_filepath,
                branch=self.github_branch
            )
            return loader.load()

        if self.bigquery_project and self.bigquery_dataset and self.bigquery_table:
            loader = BigQueryLoader(
                project=self.bigquery_project,
                dataset=self.bigquery_dataset,
                table=self.bigquery_table
            )
            return loader.load()

        if self.web_url:
            loader = WebBaseLoader(self.web_url)
            return loader.load()

        if not self.file_path:
            raise ValueError("file_path must be specified if no other data source is provided.")

        file_extension = os.path.splitext(self.file_path)[1].lower()
        loader_class = self.loader_map.get(file_extension)

        if not loader_class:
            raise ValueError(f"Unsupported file type: {file_extension}")

        if file_extension == '.json':
            loader = loader_class(
                self.file_path,
                jq_schema=self.jq_schema,
                text_content=self.json_text_content
            )
        else:
            loader = loader_class(self.file_path)

        return loader.load()

# Example Usage:
if __name__ == '__main__':
    # Example with MongoDB
    loader = DocumentLoader(
        mongo_uri="mongodb://localhost:27017",
        db_name="testdb",
        collection_name="documents",
        mongo_query={"type": "report"}
    )
    docs = loader.load()
    print(docs[0])
