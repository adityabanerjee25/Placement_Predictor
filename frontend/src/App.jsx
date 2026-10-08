import { useState } from 'react'
import './App.css'
import { createPrediction, extractDocument } from './lib/api'

const topics = [
  ['Academic performance', 'green'], ['Aptitude readiness', 'purple'], ['Technical skills', 'blue'],
  ['Internship experience', 'orange'], ['Coding practice', 'red'], ['Projects & portfolio', 'gray'],
  ['Certifications', 'green'], ['Communication', 'purple'], ['Resume intelligence', 'blue'],
  ['Career goals', 'orange'], ['Placement prep', 'red'], ['Interview confidence', 'gray'],
]
const faqs = [
  ['Is this a hiring decision?', 'No. PlacementPulse is an educational decision-support tool. Your result is an estimate based on available data, never a guarantee or a replacement for human evaluation.'],
  ['What data does the prediction use?', 'The model uses validated pre-placement academic, employability, technical, coding, project, internship and certification indicators. Post-placement fields such as salary are excluded.'],
  ['Can I upload my resume?', 'Yes. Upload a supported resume or placement form and review the fields our OCR and NLP pipeline extracts before running a prediction.'],
  ['How does the readiness score work?', 'Readiness combines the model estimate with interpretable profile signals so you can see where to focus next. It is designed for guidance, not ranking.'],
  ['Can placement cells use this for a cohort?', 'Yes, future coordinator views can support aggregate insights while keeping individual decisions with students, coordinators and recruiters.'],
]
function Mark({ children }) { return <span className="mark">{children}</span> }

const initialProfile = { ssc_p: '', hsc_p: '', degree_p: '', degree_t: 'Sci&Tech', workex: 'No', etest_p: '', project_count: '', coding_problems_solved: '' }

function IntakeModal({ onClose }) {
  const [profile, setProfile] = useState(initialProfile)
  const [result, setResult] = useState(null)
  const [extraction, setExtraction] = useState(null)
  const [extractionConfirmed, setExtractionConfirmed] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const update = (event) => setProfile({ ...profile, [event.target.name]: event.target.value })
  const submit = async (event) => {
    event.preventDefault(); setError('')
    const required = ['ssc_p', 'hsc_p', 'degree_p', 'etest_p']
    if (required.some((field) => profile[field] === '' || Number(profile[field]) < 0 || Number(profile[field]) > 100)) { setError('Add valid percentage values between 0 and 100.'); return }
    setLoading(true)
    try { setResult(await createPrediction({ ...profile, ssc_p: Number(profile.ssc_p), hsc_p: Number(profile.hsc_p), degree_p: Number(profile.degree_p), etest_p: Number(profile.etest_p), project_count: profile.project_count === '' ? null : Number(profile.project_count), coding_problems_solved: profile.coding_problems_solved === '' ? null : Number(profile.coding_problems_solved) })) } catch { setError('The prediction service is unavailable. Start the backend on port 8000 and try again.') } finally { setLoading(false) }
  }
  const upload = async (event) => {
    const file = event.target.files?.[0]
    if (!file) return
    setError('')
    try { setExtraction(await extractDocument(file)); setExtractionConfirmed(false) } catch { setError('We could not inspect that file. Try a PDF, PNG, or JPG.') }
  }
  return <div className="modal-backdrop" role="dialog" aria-modal="true" aria-label="Check your placement readiness"><div className="intake-modal"><button className="modal-close" onClick={onClose} aria-label="Close">×</button>{result ? <div className="result-view"><p className="section-kicker">YOUR READINESS SNAPSHOT</p><h2>{result.readiness.score}% <i>{result.readiness.level}</i></h2><p>{result.readiness.summary}</p><div className="result-pill">{result.prediction} estimate · {Math.round(result.probability * 100)}% probability</div><h3>What to work on next</h3><div className="suggestions">{result.suggestions.map((suggestion) => <div key={suggestion.title}><strong>{suggestion.title}</strong><p>{suggestion.reason}</p></div>)}</div><small>{result.disclaimer}</small><button className="dark-btn" onClick={() => setResult(null)}>Edit profile</button></div> : <><p className="section-kicker">START WHERE YOU ARE</p><h2>Tell us a little<br /><i>about yourself.</i></h2><p className="modal-intro">This first pass uses a deterministic demo predictor. Your answers stay in this local flow.</p><label className="upload-box">Upload a resume or form<input type="file" accept="application/pdf,image/png,image/jpeg" onChange={upload} /></label>{extraction && <div className="extraction-review"><strong>Review extracted fields</strong><span>{extraction.status === 'needs_review' ? 'Confirm the fields before continuing.' : extraction.status}</span>{extraction.fields.map((field) => <div key={field.name}><code>{field.name}</code><em>{field.needsReview ? 'Needs review' : 'Ready'}</em></div>)}<label className="confirm-extraction"><input type="checkbox" checked={extractionConfirmed} onChange={(event) => setExtractionConfirmed(event.target.checked)} /> I reviewed these extracted fields.</label></div>}<form onSubmit={submit}><div className="form-grid">{[['ssc_p','SSC %'],['hsc_p','HSC %'],['degree_p','Degree %'],['etest_p','Employability test %'],['project_count','Projects'],['coding_problems_solved','Coding problems']].map(([name,label]) => <label key={name}>{label}<input name={name} value={profile[name]} onChange={update} type="number" min="0" max={name.includes('_p') ? 100 : undefined} placeholder="0" /></label>)}</div><div className="form-grid"><label>Degree type<select name="degree_t" value={profile.degree_t} onChange={update}><option>Sci&Tech</option><option>Comm&Mgmt</option><option>Others</option></select></label><label>Work experience<select name="workex" value={profile.workex} onChange={update}><option>No</option><option>Yes</option></select></label></div>{error && <p className="form-error">{error}</p>}<button className="primary-btn" disabled={loading || (extraction && !extractionConfirmed)}>{loading ? 'Reading your profile…' : extraction && !extractionConfirmed ? 'Confirm extracted fields first' : 'See my readiness →'}</button></form></>}</div></div>
}

function App() {
  const [openFaq, setOpenFaq] = useState(null)
  const [showIntake, setShowIntake] = useState(false)
  return <main>
    <nav className="nav shell"><a className="brand" href="#top">PLACEMENT<span>PULSE</span></a><div className="nav-links"><a href="#how-it-works">How it works</a><a href="#topics">What we look at</a><a href="#faq">FAQs</a></div><button className="login-btn">Log in</button></nav>
    <section className="hero shell" id="top"><div className="doodle star star-one">✦</div><div className="doodle star star-two">✧</div><div className="doodle circle circle-one" /><div className="doodle circle circle-two" /><div className="doodle arrow arrow-one">↗</div><div className="doodle arrow arrow-two">↙</div><div className="doodle note note-one">▱</div><div className="doodle note note-two">⌁</div><p className="eyebrow">PLACEMENTPULSE</p><h1>Know where you stand.<br /><i>Grow from there.</i></h1><p className="hero-copy">A clearer view of your placement readiness — shaped by your strengths, your story, and what you can do next.</p><button className="primary-btn" onClick={() => setShowIntake(true)}>Check your readiness <span>→</span></button><p className="fine-print">It takes about 2 minutes.</p></section>
    <section className="intro shell" id="how-it-works"><p className="section-kicker">HOW IT WORKS</p><h2>From profile to possibility,<br />we make readiness feel simple.</h2><p className="section-sub">No black boxes. Just a thoughtful look at what you already bring — and the next small step worth taking.</p></section>
    <section className="steps shell">
      <article className="step"><div className="step-visual visual-profile"><div className="profile-card"><div className="avatar">AR</div><strong>Your profile</strong><span>Academics · Skills · Goals</span><div className="mini-bar"><b /></div></div><div className="spark">✦</div></div><div className="step-copy"><Mark>STEP 1</Mark><h3>Bring your whole story</h3><p>Share the academic, technical, coding and employability signals that make your profile yours. Or upload a resume and let us help fill it in.</p></div></article>
      <article className="step reverse"><div className="step-visual visual-match"><div className="score-card"><span>READINESS SNAPSHOT</span><strong>78<span>%</span></strong><div className="score-track"><b /></div><small>Looking good — with room to grow</small></div><div className="orbit orbit-a">●</div><div className="orbit orbit-b">●</div></div><div className="step-copy"><Mark>STEP 2</Mark><h3>See the bigger picture</h3><p>Our models compare your profile with patterns from placement data and return an estimate you can actually understand.</p></div></article>
      <article className="step"><div className="step-visual visual-focus"><div className="focus-card"><span>YOUR NEXT FOCUS</span><strong>Build one<br />strong project</strong><div className="focus-line" /></div><div className="doodle-arrow">↗</div></div><div className="step-copy"><Mark>STEP 3</Mark><h3>Find your next best move</h3><p>Get a short, useful list of improvement suggestions — from aptitude practice to projects, coding consistency, and more.</p></div></article>
      <article className="step reverse"><div className="step-visual visual-progress"><div className="progress-card"><span>YOUR PROGRESS</span><div className="bars"><i /><i /><i /><i /><i /></div><small>Small steps add up.</small></div><div className="heart">♡</div></div><div className="step-copy"><Mark>STEP 4</Mark><h3>Turn insight into momentum</h3><p>Come back as you grow. Track the signals that matter and walk into placement season with more clarity and confidence.</p></div></article>
    </section>
    <section className="topics shell" id="topics"><p className="section-kicker">A LITTLE MORE SIGNAL, A LOT LESS NOISE</p><h2>Everything that makes<br />you <i>you</i>.</h2><div className="topic-grid">{topics.map(([label, color]) => <span className="topic" key={label}><b className={color} />{label}</span>)}</div></section>
    <section className="audience shell"><h2>Made for every kind<br />of <i>starting point</i>.</h2><div className="audience-grid"><div><h3>Students</h3><p>Turn a vague “am I ready?” into a clear view of your strengths and next steps.</p></div><div><h3>Placement cells</h3><p>See patterns across cohorts and help more students get ready, earlier.</p></div><div><h3>Mentors & guides</h3><p>Bring a shared language to the conversations that help careers take shape.</p></div></div></section>
    <section className="faq shell" id="faq"><h2>Frequently Asked Questions</h2><div className="faq-list">{faqs.map(([question, answer], index) => <div className={`faq-item ${openFaq === index ? 'open' : ''}`} key={question}><button onClick={() => setOpenFaq(openFaq === index ? null : index)}><span>{question}</span><b>⌄</b></button>{openFaq === index && <p>{answer}</p>}</div>)}</div></section>
    <section className="cta shell"><div className="cta-spark">✦</div><h2>Start with where<br />you are.</h2><p>It takes 2 minutes to get a clearer picture. It takes a little curiosity to make it useful.</p><button className="dark-btn" onClick={() => setShowIntake(true)}>Check your readiness <span>→</span></button></section>
    <footer className="footer shell"><a className="brand light" href="#top">PLACEMENT<span>PULSE</span></a><div><a href="#faq">FAQs</a><a href="#how-it-works">How it works</a><a href="#topics">Privacy & responsible use</a></div><small>Built for better beginnings · 2026</small></footer>
    {showIntake && <IntakeModal onClose={() => setShowIntake(false)} />}
  </main>
}
export default App
