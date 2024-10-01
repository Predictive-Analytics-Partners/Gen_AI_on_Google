import numpy as np
import glob
from typing import List
from typing import Optional
import vertexai
from vertexai.vision_models import (
    Image,
    MultiModalEmbeddingModel,
    MultiModalEmbeddingResponse,
)
from google.cloud import storage


def get_image_embeddings(image_path):
    """Generate embeddings for a given image.

    Args:
        image_path: Path to the image file.

    Returns:
        The image embedding as a numpy array.
    """
    model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding")
    embeddings = model.get_embeddings(image=image_path)
    return embeddings


gcs_bucket_name = "ladd-pdf-uploads"
gcs_image_prefix = "Doc1/Doc1_images/"

storage_client = storage.Client()
bucket = storage_client.bucket(gcs_bucket_name)

blobs = bucket.list_blobs(prefix=gcs_image_prefix)

for blob in blobs:
    if blob.name.endswith('/'):  # Skip directories if any
        continue

    file_name = blob.name.encode(encoding="UTF-8", errors="strict")

    # get GCS URI (use the full blob name, not the directory)
    gcs_uri = f"gs://{gcs_bucket_name}/{blob.name}"
    print(gcs_uri)

    img = Image(gcs_uri=gcs_uri)
    embeddings = get_image_embeddings(img)

    with open("indexData.json", "a") as f:
        f.write('{"id":"' + str(file_name) + '",')
        f.write(
            '"embedding":['
            + ",".join(str(x) for x in embeddings.image_embedding)
            + "]}"
        )
        f.write("\n")
