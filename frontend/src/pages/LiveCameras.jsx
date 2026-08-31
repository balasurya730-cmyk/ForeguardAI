import { useState, useEffect } from 'react'
import { Camera, Radio, Maximize2, ShieldAlert, Power, PowerOff } from 'lucide-react'

export default function LiveCameras() {
  const [streamError, setStreamError] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [aiEnabled, setAiEnabled] = useState(true)

  // This relies on the Python run_live_stream.py script running on port 8002
  const STREAM_URL = "http://127.0.0.1:8002/video_feed"

  useEffect(() => {
    fetch('http://127.0.0.1:8002/api/detection_status')
      .then(res => res.json())
      .then(data => setAiEnabled(data.ai_enabled))
      .catch(console.error)
  }, [])

  const toggleAi = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8002/api/toggle_detection', { method: 'POST' })
      const data = await res.json()
      setAiEnabled(data.ai_enabled)
    } catch (e) {
      console.error(e)
    }
  }

  const toggleFullscreen = () => {
    const elem = document.getElementById('camera-feed')
    if (!document.fullscreenElement) {
      elem.requestFullscreen().catch(err => {
        console.error(`Error attempting to enable fullscreen: ${err.message}`)
      })
      setIsFullscreen(true)
    } else {
      document.exitFullscreen()
      setIsFullscreen(false)
    }
  }

  // Handle escape key for fullscreen state
  useEffect(() => {
    const handleFullscreenChange = () => setIsFullscreen(!!document.fullscreenElement)
    document.addEventListener('fullscreenchange', handleFullscreenChange)
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange)
  }, [])

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink-900">Live Camera Feeds</h1>
          <p className="text-sm text-ink-500 mt-0.5">Real-time AI video streaming and detection</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 bg-signal-cyan/10 border border-signal-cyan/20 rounded-md">
          <Radio size={14} className="text-signal-cyan animate-pulse" />
          <span className="text-xs font-mono font-medium text-signal-cyan">MJPEG STREAM ACTIVE</span>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Main Camera Feed */}
        <div className="lg:col-span-2">
          <div className="panel overflow-hidden border-signal-cyan/30 shadow-[0_0_20px_rgba(4,217,255,0.05)]">
            <div className="p-3 border-b border-base-600 flex justify-between items-center bg-base-800">
              <div className="flex items-center gap-2">
                <Camera size={16} className="text-ink-500" />
                <h3 className="font-display font-semibold text-sm text-ink-900">CAM-01: Assembly Line Alpha</h3>
              </div>
              <button 
                onClick={toggleFullscreen}
                className="p-1 text-ink-500 hover:text-signal-cyan hover:bg-signal-cyan/10 rounded transition-colors"
                title="Fullscreen"
              >
                <Maximize2 size={16} />
              </button>
            </div>
            <div 
              id="camera-feed"
              className="aspect-video bg-black relative flex items-center justify-center overflow-hidden"
            >
              {streamError ? (
                <div className="text-center p-6 space-y-4">
                  <ShieldAlert size={48} className="mx-auto text-signal-red/70" />
                  <div>
                    <h4 className="text-ink-900 font-medium">Stream Offline</h4>
                    <p className="text-sm text-ink-500 mt-1 max-w-sm mx-auto">
                      Cannot connect to the live AI camera on port 8002. Make sure you are running 
                      <code className="text-signal-cyan bg-signal-cyan/10 px-1 py-0.5 rounded mx-1">python ai_engine/run_live_stream.py</code>
                    </p>
                  </div>
                </div>
              ) : (
                <>
                  <img
                    src={STREAM_URL}
                    alt="Live AI Camera Feed"
                    className="w-full h-full object-cover"
                    onError={() => setStreamError(true)}
                  />
                  {/* Overlay UI elements that will also show in fullscreen */}
                  <div className="absolute top-4 right-4 flex items-center gap-2 bg-black/60 backdrop-blur px-2 py-1 rounded text-[10px] font-mono text-white">
                    <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                    LIVE REC
                  </div>
                  <div className={`absolute bottom-4 left-4 bg-black/60 backdrop-blur px-2 py-1 rounded text-[10px] font-mono ${aiEnabled ? 'text-signal-cyan' : 'text-ink-500'}`}>
                    {aiEnabled ? 'AI YOLOv8 ENGINE ACTIVE · 19 CLASSES' : 'AI ENGINE PAUSED · RAW FEED'}
                  </div>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Sidebar Information */}
        <div className="space-y-6">
          <div className="panel p-5">
            <h3 className="font-display font-semibold text-sm text-ink-900 mb-4 border-b border-base-600 pb-2">Camera Information</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-ink-500">Location</span>
                <span className="text-ink-900 font-medium">Zone A / Assembly</span>
              </div>
              <div className="flex justify-between">
                <span className="text-ink-500">Resolution</span>
                <span className="text-ink-900 font-medium">1080p (Scaled)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-ink-500">Protocol</span>
                <span className="text-ink-900 font-medium">MJPEG / HTTP</span>
              </div>
              <div className="flex justify-between">
                <span className="text-ink-500">AI Model</span>
                <span className="text-ink-900 font-medium text-signal-cyan">YOLOv8 Custom</span>
              </div>
            </div>
            
            <button 
              onClick={toggleAi} 
              className={`mt-4 w-full flex items-center justify-center gap-2 py-2 rounded-md text-sm font-medium transition-colors border ${
                aiEnabled 
                  ? 'bg-signal-red/10 text-signal-red border-signal-red/30 hover:bg-signal-red/20' 
                  : 'bg-signal-cyan/10 text-signal-cyan border-signal-cyan/30 hover:bg-signal-cyan/20'
              }`}
            >
              {aiEnabled ? <PowerOff size={16} /> : <Power size={16} />}
              {aiEnabled ? 'Turn Off AI Detection' : 'Turn On AI Detection'}
            </button>
          </div>

          <div className="panel p-5">
            <h3 className="font-display font-semibold text-sm text-ink-900 mb-4 border-b border-base-600 pb-2">AI Color Legend</h3>
            <div className="space-y-3 text-sm">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <span className="text-ink-500">Safety Hazards</span>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-green-500" />
                <span className="text-ink-500">Compliant PPE</span>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-gray-500" />
                <span className="text-ink-500">Neutral Objects</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
