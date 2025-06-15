import { useState } from "react";
import axios from "axios";

function App() {
  const [url, setUrl] = useState("");
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [isCrawled, setIsCrawled] = useState(false);
  const [debugInfo, setDebugInfo] = useState("");
  const [crawledUrls, setCrawledUrls] = useState([]); // New state for crawled URLs

  const handleCrawl = async () => {
    if (!url.trim()) {
      setStatus("❌ Please enter a valid URL");
      return;
    }

    try {
      setLoading(true);
      setStatus("🔍 Crawling and indexing website...");
      setMessages([]);
      setDebugInfo("Sending crawl request...");
      setCrawledUrls([]); // Clear previous URLs
      
      console.log("Crawling URL:", url.trim());
      
      const res = await axios.post("http://localhost:8000/crawl", {
        url: url.trim(),
        max_pages: 15,
      }, {
        timeout: 30000,
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      console.log("Crawl response:", res.data);
      
      // Extract crawled URLs from response
      if (res.data.crawled_urls) {
        setCrawledUrls(res.data.crawled_urls);
      } else if (res.data.urls) {
        setCrawledUrls(res.data.urls);
      } else {
        // Fallback - at least show the main URL
        setCrawledUrls([url.trim()]);
      }
      
      setDebugInfo(`Crawl successful: ${JSON.stringify(res.data)}`);
      setStatus("✅ Website crawled successfully! You can now ask questions.");
      setIsCrawled(true);
      
    } catch (err) {
      console.error("Crawl error details:", err);
      setDebugInfo(`Crawl error: ${err.message} - ${err.response?.data || 'No response data'}`);
      
      if (err.code === 'ECONNREFUSED') {
        setStatus("❌ Cannot connect to server. Make sure your backend is running on localhost:8000");
      } else if (err.response) {
        setStatus(`❌ Server error: ${err.response.status} - ${err.response.data?.detail || err.response.statusText}`);
      } else if (err.request) {
        setStatus("❌ No response from server. Check your backend connection.");
      } else {
        setStatus(`❌ Error: ${err.message}`);
      }
      setIsCrawled(false);
      setCrawledUrls([]);
    } finally {
      setLoading(false);
    }
  };

  const handleAsk = async () => {
    if (!question.trim()) {
      setStatus("❌ Please enter a question");
      return;
    }

    if (!isCrawled) {
      setStatus("❌ Please crawl a website first before asking questions");
      return;
    }

    const trimmedQuestion = question.trim();

    try {
      setLoading(true);
      setStatus("💬 Getting AI response...");
      setDebugInfo("Sending question to AI...");
      
      const userMessage = { type: 'user', content: trimmedQuestion };
      setMessages(prev => [...prev, userMessage]);
      
      const res = await axios.post("http://localhost:7071/api/ask", {
        question: trimmedQuestion,
      }, {
        timeout: 60000,
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      let answer;
      
      if (typeof res.data === 'string') {
        answer = res.data;
      } else if (res.data && typeof res.data === 'object') {
        if (res.data.answer) {
          answer = res.data.answer;
        } else if (res.data.response) {
          answer = res.data.response;
        } else {
          const stringFields = Object.keys(res.data).filter(key => 
            typeof res.data[key] === 'string' && res.data[key].length > 10
          );
          if (stringFields.length > 0) {
            answer = res.data[stringFields[0]];
          }
        }
      }
      
      if (!answer) {
        setStatus("❌ No answer received from AI");
        setDebugInfo(`Response structure: ${JSON.stringify(res.data)}`);
        return;
      }
      
      setDebugInfo(`AI response received: ${answer.substring(0, 100)}...`);
      
      const aiMessage = { type: 'ai', content: answer };
      setMessages(prev => [...prev, aiMessage]);
      
      setQuestion("");
      setStatus("✅ Response received!");
      
    } catch (err) {
      console.error("Error in handleAsk:", err);
      setDebugInfo(`Ask error: ${err.message}`);
      
      if (err.code === 'ECONNREFUSED') {
        setStatus("❌ Cannot connect to server. Make sure your backend is running.");
      } else if (err.response) {
        setStatus(`❌ Server error: ${err.response.status} - ${err.response.data?.detail || err.response.statusText}`);
      } else if (err.request) {
        setStatus("❌ No response from server. Request timed out or failed.");
      } else {
        setStatus(`❌ Error: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e, action) => {
    if (e.key === 'Enter') {
      action();
    }
  };

  // Function to render message with clickable links
  const renderMessageWithLinks = (content) => {
  // Simple approach: just look for markdown links
  const parts = content.split(/(\[[^\]]+\]\([^)]+\))/g);
  
  return parts.map((part, index) => {
    const markdownMatch = part.match(/\[([^\]]+)\]\(([^)]+)\)/);
    
    if (markdownMatch) {
      const [, linkText, url] = markdownMatch;
      return (
        <button
          key={index}
          onClick={() => {
            console.log("Opening URL:", url);
            window.open(url, '_blank');
          }}
          className="inline bg-blue-600 hover:bg-blue-700 text-white px-2 py-1 rounded text-xs mx-1 cursor-pointer"
          style={{ display: 'inline-block' }}
        >
          🔗 {linkText}
        </button>
      );
    }
    
    return <span key={index}>{part}</span>;
  });
};

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black">
      {/* Header */}
     {/* Header */}
<div className="bg-gray-800/50 backdrop-blur-sm border-b border-gray-700">
  <div className="max-w-6xl mx-auto px-4 py-6">
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
          🧠 AI Website Chat
        </h1>
        <p className="text-gray-400 mt-2">
          Crawl any website and chat with its content using AI
        </p>
      </div>
      <div className="text-right">
        <div className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400">
          NEXORA
        </div>
        <p className="text-gray-500 text-sm">nexorahq.tech</p>
      </div>
    </div>
  </div>
</div>

      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - URL Input and Crawled URLs */}
          <div className="lg:col-span-1 space-y-6">
            {/* URL Input Section */}
            <div className="bg-gray-800/70 backdrop-blur-sm p-6 rounded-2xl shadow-2xl border border-gray-700">
              <div className="flex items-center mb-4">
                <span className="text-2xl mr-2">🌐</span>
                <h2 className="text-xl font-semibold text-white">Website URL</h2>
                {isCrawled && <span className="ml-2 text-green-400 text-sm">✅ Crawled</span>}
              </div>
              
              <div className="space-y-3">
                <input
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  onKeyPress={(e) => handleKeyPress(e, handleCrawl)}
                  className="w-full bg-gray-700 border border-gray-600 text-white px-4 py-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder-gray-400"
                  placeholder="https://example.com"
                  disabled={loading}
                />
                <button
                  onClick={handleCrawl}
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
                >
                  {loading ? "Crawling..." : "Crawl Website"}
                </button>
              </div>
            </div>

            {/* Crawled URLs Section */}
            {crawledUrls.length > 0 && (
              <div className="bg-gray-800/70 backdrop-blur-sm p-6 rounded-2xl shadow-2xl border border-gray-700">
                <div className="flex items-center mb-4">
                  <span className="text-2xl mr-2">📄</span>
                  <h2 className="text-lg font-semibold text-white">Crawled Pages</h2>
                  <span className="ml-2 bg-blue-600 text-white text-xs px-2 py-1 rounded-full">
                    {crawledUrls.length}
                  </span>
                </div>
                
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {crawledUrls.map((crawledUrl, index) => (
                    <div key={index} className="bg-gray-700/50 p-3 rounded-lg border border-gray-600">
                      <div className="flex items-center justify-between">
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-gray-300 truncate" title={crawledUrl}>
                            {crawledUrl}
                          </p>
                        </div>
                        <button
                          onClick={() => window.open(crawledUrl, '_blank')}
                          className="ml-2 bg-blue-600 hover:bg-blue-700 text-white p-1 rounded text-xs transition-colors"
                          title="Open in new tab"
                        >
                          🔗
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Debug Info Panel */}
            {/* {debugInfo && (
              <div className="bg-gray-900 p-4 rounded-lg border border-gray-600">
                <h3 className="text-sm font-semibold text-yellow-400 mb-2">Debug Info:</h3>
                <p className="text-xs text-gray-300 font-mono break-words">{debugInfo}</p>
              </div>
            )} */}
          </div>

          {/* Right Column - Chat Interface */}
          <div className="lg:col-span-2">
            {/* Status Display */}
            {status && (
              <div className="bg-gray-800/50 backdrop-blur-sm p-4 rounded-lg border border-gray-700 mb-6">
                <p className="text-gray-300 text-center">{status}</p>
              </div>
            )}

            {/* Chat Section */}
            <div className="bg-gray-800/70 backdrop-blur-sm rounded-2xl shadow-2xl border border-gray-700 overflow-hidden">
              {/* Chat Header */}
              <div className="bg-gray-700/50 p-4 border-b border-gray-600">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <span className="text-2xl mr-2">💬</span>
                    <h2 className="text-xl font-semibold text-white">Chat with Website</h2>
                  </div>
                  {messages.length > 0 && (
                    <span className="bg-green-600 text-white text-xs px-2 py-1 rounded-full">
                      {messages.length} messages
                    </span>
                  )}
                </div>
              </div>

              {/* Messages Area */}
              <div className="h-96 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 ? (
                  <div className="text-center text-gray-500 mt-20">
                    <div className="text-6xl mb-4">🤖</div>
                    <p>Crawl a website first, then start asking questions!</p>
                    <p className="text-xs mt-2 text-gray-600">
                      {crawledUrls.length} pages ready for questions
                    </p>
                  </div>
                ) : (
                  messages.map((message, index) => (
                    <div
                      key={index}
                      className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-lg px-4 py-3 rounded-2xl ${
                          message.type === 'user'
                            ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white'
                            : 'bg-gray-700 text-gray-100 border border-gray-600'
                        }`}
                      >
                        <div className="flex items-start gap-2">
                          <span className="text-lg flex-shrink-0 mt-1">
                            {message.type === 'user' ? '👤' : '🤖'}
                          </span>
                          <div className="text-sm leading-relaxed">
                            {message.type === 'ai' 
                              ? renderMessageWithLinks(message.content)
                              : message.content
                            }
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>

              {/* Input Area */}
              <div className="bg-gray-700/50 p-4 border-t border-gray-600">
                <div className="flex gap-3">
                  <input
                    type="text"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyPress={(e) => handleKeyPress(e, handleAsk)}
                    className="flex-1 bg-gray-600 border border-gray-500 text-white px-4 py-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent placeholder-gray-400"
                    placeholder="Ask a question about the website..."
                    disabled={loading || !isCrawled}
                  />
                  <button
                    onClick={handleAsk}
                    disabled={loading || !isCrawled}
                    className="bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
                  >
                    {loading ? "..." : "Ask AI"}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        {/* Footer */}
<div className="mt-8 text-center text-gray-500 text-sm space-y-2">
  <p>
    Powered by <span className="text-purple-400 font-semibold">Nexora</span> • 
    Built with React & Tailwind CSS
  </p>
  <p>
    <a 
      href="https://nexorahq.tech" 
      target="_blank" 
      rel="noopener noreferrer"
      className="text-blue-400 hover:text-blue-300 transition-colors"
    >
      nexorahq.tech
    </a>
    {" • "}
    <span className="text-gray-600">© 2025 Nexora. All rights reserved.</span>
  </p>
</div>
      </div>
    </div>
  );
}

export default App;