import { render, screen } from "@testing-library/react"
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "./table.js"
import { describe, it, expect } from "vitest"
/// <reference types="@testing-library/jest-dom" />

describe("Table", () => {
  it("renders header and cell", () => {
    render(
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow>
            <TableCell>Alice</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    )
    expect(screen.getByText("Name")).toBeInTheDocument()
    expect(screen.getByText("Alice")).toBeInTheDocument()
  })
})
