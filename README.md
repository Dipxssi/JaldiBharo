#  JaldiBharo: AI-Powered Marketplace Listing


##  Technical Overview
**JaldiBharo** automates the tedious process of manual data entry for e-commerce sellers. By leveraging **Gemini 1.5 Flash**, the system "sees" product images to automatically categorize items, suggest competitive pricing, and generate SEO-optimized tags, reducing listing time by ~90%.

##  The Stack
* **Backend:** FastAPI (Python)
* **AI:** Google Gemini 1.5 Flash (**Native Multimodal** Vision + Structured Output)
* **Database:** NeonDB (Serverless PostgreSQL)
* **ORM:** SQLModel (Pydantic + SQLAlchemy)
* **Storage:** Cloudinary (Image Blob Storage)
* **Image Processing:** Pillow (PIL) for custom collage logic
* **Environment:** Managed via `uv` 



## System Architecture


1.  **Image Aggregation:** Users upload multiple angles of a physical product.
2.  **Collage Optimization:** To optimize token usage and provide global context to the LLM, the backend stitches images into a **2x2 grid** using Pillow. This ensures the model sees the "whole" item in a single inference pass.
3.  **Vision Inference:** The collage is sent to Gemini 1.5 Flash with a strict Pydantic-enforced JSON schema.
4.  **Persistent Storage:** Images are hosted on Cloudinary; metadata and AI-generated fields are persisted in NeonDB via a **UUID-based** relational schema.

---
