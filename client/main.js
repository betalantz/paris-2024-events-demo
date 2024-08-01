import './style.css'
import faunadb from 'faunadb'
import {query as q } from 'faunadb'

const client = new faunadb.Client({ secret: import.meta.env.VITE_FAUNA_SECRET })

document.querySelector('#app').innerHTML = `
  <div>
    
    <h1>Fauna Test</h1>
    
  </div>
`

async function getAllEvents(req, res) {
  try {
    const events = await client.query(
      q.Map(
        q.Paginate(q.Documents(q.Collection('Events'))),
        q.Lambda(x => q.Get(x))
      )
    )
    return res.status(200).json(events.data)
  } catch (e) {
    return res.status(500).json({ error: e.message })
  }
}

getAllEvents({}, {
  status: function(statusCode) {
    return {
      json: function(data) {
        console.log(data)
      }
    }
  }
})