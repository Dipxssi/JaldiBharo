import { useState } from 'react'

function App() {
  const [files, setFiles] = useState([])
  const [previews, setPreviews] = useState([]);
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  const onFileChange = (e) => {
    const newSelectedFiles = Array.from(e.target.files);
    setFiles((prevFiles) => [...prevFiles , ...newSelectedFiles]);

    const newPreviewUrls = newSelectedFiles.map(file => URL.createObjectURL(file));
    setPreviews((prevPreviews) => [...prevPreviews, ...newPreviewUrls]);
  };

  const handleUpload = async () => {
    if (files.length === 0) return alert("Please seelct images! ")

    setLoading(true);

    const formData = new FormData();

    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i])

    }
    try {
      const response = await fetch('http://127.0.0.1:8000/upload', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const message = await response.text();
        throw new Error(message || `HTTP ${response.status}`);
      }
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error("Upload failed:", error)
      alert("Something went wrong!")
    } finally {
      setLoading(false)
    }

  }

  

  return (
    <div style={{
      padding: '40px',
      fontFamily: 'sans-serif'
    }}>
      <h1>JaldiBharo AI</h1>
      <input type="file" multiple onChange={onFileChange} accept="image/*" />

      <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
        {previews.map((url, i) => (
          <img key={i} src={url} style={{ width: '100px', height: '100px', objectFit: 'cover', borderRadius: '8px', border: '2px solid #555' }} />
        ))}
      </div>

      <button onClick={handleUpload} disabled={loading} style={{
        marginLeft: '10px '
      }}>{loading ? "AI is thinking" : "Upload & Generate Listing"}</button>
      {result && (
        <div style={{ marginTop: '20px', border: '1px solid #ccc', padding: '20px' }}>
          <h2>AI Generated Result:</h2>
          <img src={result.image_url} alt="Collage" style={{ width: '300px' }} />
          <p><strong>Title:</strong> {result.title}</p>
          <p><strong>Price:</strong> ${result.suggested_price}</p>
          <p><strong>Category:</strong> {result.category}</p>
          <p><strong>Tags:</strong> {result.tags}</p>
        </div>
      )}
    </div>
  )
}

export default App;