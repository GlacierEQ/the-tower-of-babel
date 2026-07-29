CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS embeddings (id UUID PRIMARY KEY, vec vector(1536));
CREATE INDEX ON embeddings USING hnsw (vec vector_cosine_ops);
