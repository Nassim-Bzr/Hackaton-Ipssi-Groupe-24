import { NavLink } from "react-router-dom"

export function Navbar() {
  return (
    <nav className="flex items-center gap-4 border-b pb-4 fixed top-5 bg-background">
      <NavLink
        to="/"
        className={({ isActive }) =>
          `hover:underline ${isActive ? "underline" : ""}`
        }
      >
        Upload PDF
      </NavLink>
      <NavLink
        to="/documents"
        className={({ isActive }) =>
          `hover:underline ${isActive ? "underline" : ""}`
        }
      >
        Tous les documents
      </NavLink>
    </nav>
  )
}

