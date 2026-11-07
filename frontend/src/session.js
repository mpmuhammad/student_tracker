import { reactive } from 'vue'
import { call } from 'frappe-ui'

// Shared session state for the mentor portal.
export const session = reactive({
  loaded: false,
  user: 'Guest',
  fullName: '',
  userImage: null,
  isMentor: false,
  get isLoggedIn() {
    return this.user && this.user !== 'Guest'
  },
})

export async function loadSession() {
  try {
    const info = await call('student_tracker.api.get_session_info')
    session.user = info.user
    session.fullName = info.full_name || ''
    session.userImage = info.user_image || null
    session.isMentor = !!info.is_mentor
  } catch (e) {
    session.user = 'Guest'
    session.isMentor = false
  }
  session.loaded = true
  return session
}

export async function login(email, password) {
  await call('login', { usr: email, pwd: password })
  // Full reload so the page gets a fresh CSRF token for the new session.
  window.location.href = '/mentor'
}

export async function logout() {
  await call('logout')
  window.location.href = '/login'
}
