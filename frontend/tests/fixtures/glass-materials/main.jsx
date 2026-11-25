import React from 'react'
import{createRoot}from'react-dom/client'
import '../../../src/styles/v2-tokens.css'
import '../../../src/styles/liquid-surfaces.css'
import '../../../src/styles/glass-materials.css'
import GlassOptics from '../../../src/components/GlassOptics'
import './style.css'
const theme=new URLSearchParams(location.search).get('theme')||'light'
document.documentElement.dataset.theme=theme
createRoot(document.getElementById('root')).render(<><GlassOptics/><div className="lab-pattern" aria-hidden="true"/><main className="material-lab"><h1>Local material lab</h1><p>Optical test pattern, not a platform screen. Original geometry; no user data.</p><div className="glass-workspace"><h2>A · Workspace</h2><p>Background influence with a comfortable text layer.</p><section className="glass-panel"><h2>B · Frost</h2><p>Grouped content inside one workspace backdrop.</p></section></div><nav className="site-header"><span>C · Optical backplate</span><button className="theme-toggle" type="button">Focus</button></nav><article className="glass-reading"><h2>D · Reading</h2><p>Long content and critical forms retain a dense, stable surface.</p></article></main></>)
