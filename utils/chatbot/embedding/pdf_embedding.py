import os
from langchain_openai import OpenAIEmbeddings
from django.core.files.storage import default_storage

from langchain_community.document_loaders import PDFPlumberLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.storage import LocalFileStore
from langchain.embeddings import CacheBackedEmbeddings

from langchain_community.vectorstores import FAISS

embed_model = "text-embedding-3-small"  # $0.020 / 1M tokens
# embed_model = "text-embedding-3-large"    # $0.130 / 1M tokens
# embed_model = "text-embedding-ada-002"    # $0.100 / 1M tokens


class Embedder:
    def __init__(self):
        pass

    def embed(self, username, file):
        # store file
        file_path = f"./.cache/{username}/file/{file.name}"
        full_path = os.path.join(os.getcwd(), file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with default_storage.open(full_path, "wb+") as definition:
            for chunk in file.chunks():
                definition.write(chunk)

        # load file
        loader = PDFPlumberLoader(file_path)

        # split text
        splitter = CharacterTextSplitter.from_tiktoken_encoder(
            separator="\n",
            chunk_size=600,
            chunk_overlap=100,
        )
        docs = loader.load_and_split(text_splitter=splitter)

        # embed file
        embed_path = f"./.cache/{username}/embeddings/{file.name}"
        embeddings = OpenAIEmbeddings(model=embed_model)
        folder_path = os.path.dirname(embed_path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # cache embeddings
        cache_dir = LocalFileStore(embed_path)
        cache_embeddings = CacheBackedEmbeddings.from_bytes_store(embeddings, cache_dir)

        # generate embeddings : it costs money when if there is no cache!
        FAISS.from_documents(docs, cache_embeddings)

        return {
            "file_path": file_path,
            "embed_path": embed_path,
        }

    def load(self, embed_path, file_path):
        # load file
        loader = PDFPlumberLoader(file_path)

        # split text
        splitter = CharacterTextSplitter.from_tiktoken_encoder(
            separator="\n",
            chunk_size=600,
            chunk_overlap=100,
        )
        docs = loader.load_and_split(text_splitter=splitter)

        embeddings = OpenAIEmbeddings(model=embed_model)
        cache_dir = LocalFileStore(embed_path)
        cache_embeddings = CacheBackedEmbeddings.from_bytes_store(embeddings, cache_dir)

        # load cached embeddings
        # vectorstores = FAISS(cache_embeddings)
        return FAISS.from_documents(docs, cache_embeddings).as_retriever()
