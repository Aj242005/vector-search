import { useState } from 'react'
import axios from 'axios'
import { UploadCloud, Image as ImageIcon, Loader2, Download } from 'lucide-react'

function App() {
  const [file, setFile] = useState(null)
  const [phoneNumber, setPhoneNumber] = useState('')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file || !phoneNumber) {
      setError("Please provide both an image and a phone number.")
      return
    }

    setLoading(true)
    setError(null)
    setResults(null)

    const formData = new FormData()
    formData.append('file', file)
    formData.append('phone_number', phoneNumber)

    try {
      // Pointing to the backend running on port 1008
      const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:1008'
      const response = await axios.post(`${backendUrl}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      if (response.data.status === 'success') {
        setResults(response.data.matches)
      } else {
        setError(response.data.message || "An error occurred.")
      }
    } catch (err) {
      console.error(err)
      setError(err.response?.data?.detail || "Failed to upload to the server. Please ensure the backend is running.")
    } finally {
      setLoading(false)
    }
  }

  const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:1008'

  const handleDownloadAll = async () => {
    if (!results || results.length === 0) return;
    
    try {
      const filenames = results.map(r => r.metadata?.filename).filter(Boolean);
      const response = await axios.post(`${backendUrl}/download-zip`, filenames, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'similar_images.zip');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error("Error downloading zip:", err);
      alert("Failed to download images as zip.");
    }
  };



  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8 bg-white p-10 rounded-2xl shadow-xl border border-gray-100">
        <div>
          <h2 className="mt-2 text-center text-3xl font-bold text-red-600 tracking-tight">
            Image Similarity Search
          </h2>
          <p className="mt-2 text-center text-sm text-gray-500">
            Upload an image to find similar images from the drive
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 text-red-700 p-3 rounded-lg text-sm border border-red-200">
              {error}
            </div>
          )}

          <div className="rounded-md shadow-sm space-y-4">
            <div>
              <label htmlFor="phone-number" className="block text-sm font-medium text-gray-700">
                Phone Number
              </label>
              <input
                id="phone-number"
                name="phone-number"
                type="tel"
                required
                className="appearance-none relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-lg focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm mt-1 bg-gray-50 transition-colors"
                placeholder="+1 (555) 000-0000"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Image Upload
              </label>
              <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-lg hover:border-indigo-500 transition-colors bg-gray-50 group cursor-pointer relative">
                <div className="space-y-1 text-center">
                  {file ? (
                    <div className="flex flex-col items-center">
                      <ImageIcon className="mx-auto h-12 w-12 text-indigo-500" />
                      <p className="text-sm text-gray-600 mt-2 font-medium">{file.name}</p>
                    </div>
                  ) : (
                    <>
                      <UploadCloud className="mx-auto h-12 w-12 text-gray-400 group-hover:text-indigo-500 transition-colors" />
                      <div className="flex text-sm text-gray-600 justify-center">
                        <span className="relative cursor-pointer bg-transparent rounded-md font-medium text-indigo-600 hover:text-indigo-500 focus-within:outline-none">
                          <span>Upload a file</span>
                        </span>
                        <p className="pl-1">or drag and drop</p>
                      </div>
                      <p className="text-xs text-gray-500">
                        PNG, JPG, JPEG up to 10MB
                      </p>
                    </>
                  )}
                </div>
                <input 
                  id="file-upload" 
                  name="file-upload" 
                  type="file" 
                  accept="image/png, image/jpeg, image/jpg"
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" 
                  onChange={handleFileChange}
                />
              </div>
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-70 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <Loader2 className="animate-spin h-5 w-5" /> Processing...
                </span>
              ) : (
                'Search Similar Images'
              )}
            </button>
          </div>
        </form>
      </div>

      {results && (
        <div className="w-full max-w-4xl mt-12 bg-white p-8 rounded-2xl shadow-lg border border-gray-100">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-2xl font-bold text-gray-900">Results</h3>
            {results.length > 0 && (
              <button 
                onClick={handleDownloadAll}
                className="flex items-center gap-2 bg-indigo-50 text-indigo-700 px-4 py-2 rounded-lg font-medium hover:bg-indigo-100 transition-colors"
              >
                <Download className="w-4 h-4" /> Download All as ZIP
              </button>
            )}
          </div>
          {results.length === 0 ? (
            <p className="text-gray-500 text-center py-10 bg-gray-50 rounded-lg">No similar images found in the database.</p>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
              {results.map((match, idx) => (
                <div key={idx} className="bg-gray-50 rounded-xl overflow-hidden shadow-sm border border-gray-100 hover:shadow-md transition-shadow flex flex-col">
                  <div className="h-48 bg-gray-200 flex items-center justify-center relative overflow-hidden group">
                    {match.metadata?.filename ? (
                      <img 
                        src={`${backendUrl}/images/${encodeURIComponent(match.metadata.filename)}`} 
                        alt="Similar match" 
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                        onError={(e) => {
                          e.target.style.display = 'none';
                          e.target.nextSibling.style.display = 'flex';
                        }}
                      />
                    ) : null}
                    <div className="absolute inset-0 items-center justify-center bg-gray-800 text-white p-4 text-center break-words" style={{display: match.metadata?.filename ? 'none' : 'flex'}}>
                      {match.metadata?.filename || "No Image"}
                    </div>
                  </div>
                  <div className="p-5 flex-grow flex flex-col justify-between">
                    <div>
                      <p className="text-sm font-semibold text-gray-900 truncate" title={`ID: ${match.id}`}>ID: {match.id.substring(0, 15)}...</p>
                      <div className="mt-2 flex items-center gap-2">
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div className="bg-indigo-600 h-2 rounded-full" style={{ width: `${Math.min(100, match.score * 100)}%` }}></div>
                        </div>
                        <span className="text-xs font-medium text-gray-500">{(match.score * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                    {match.metadata?.filename && (
                      <a 
                        href={`${backendUrl}/download/${encodeURIComponent(match.metadata.filename)}`}
                        className="mt-4 flex items-center justify-center gap-2 w-full py-2 border border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-100 transition-colors"
                      >
                        <Download className="w-4 h-4" /> Download
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Footer */}
      <footer className="w-full max-w-4xl mt-auto pt-16 pb-8 flex flex-col items-center justify-center gap-4">
        <div className="flex items-center gap-3 bg-white px-6 py-3 rounded-full shadow-sm border border-gray-100">
          <img src="https://ik.imagekit.io/evkfzbhzw/image.png?updatedAt=1776620396317" alt="Akshit Jain" className="w-10 h-10 rounded-full shadow-sm object-cover" />
          <div className="text-left leading-tight">
            <p className="text-sm font-bold text-gray-900">Made with ❤️</p>
            <p className="text-xs text-gray-500 font-medium">By <b>Akshit Jain</b></p>
          </div>
        </div>
        <div className="flex items-center gap-6 mt-2">
          <a href="https://www.linkedin.com/in/akshitjain24/" target="_blank" rel="noopener noreferrer" className="text-sm font-medium text-gray-500 hover:text-indigo-600 transition-colors flex items-center gap-1">
            LinkedIn
          </a>
          <a href="https://github.com/Aj242005" target="_blank" rel="noopener noreferrer" className="text-sm font-medium text-gray-500 hover:text-gray-900 transition-colors flex items-center gap-1">
            GitHub
          </a>
        </div>
      </footer>
    </div>
  )
}

export default App
