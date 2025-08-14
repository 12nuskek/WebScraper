import { NextResponse } from "next/server";

export async function POST(request: Request) {
  const body = await request.json().catch(() => ({}));
  const { email, password } = body as { email?: string; password?: string };

  if (!email || !password) {
    return new Response(JSON.stringify({ detail: "Email and password are required" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

  const backendResponse = await fetch(`${apiBaseUrl}/auth/login/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  const data = await backendResponse.json().catch(() => null);

  if (!backendResponse.ok) {
    return new Response(JSON.stringify(data || { detail: "Login failed" }), {
      status: backendResponse.status,
      headers: { "Content-Type": "application/json" },
    });
  }

  // Expecting { access, refresh, user }
  const accessToken = data?.access as string | undefined;
  const refreshToken = data?.refresh as string | undefined;

  const response = NextResponse.json({ ok: true });
  if (accessToken) {
    response.cookies.set("access_token", accessToken, {
      httpOnly: true,
      sameSite: "lax",
      path: "/",
      secure: process.env.NODE_ENV === "production",
      maxAge: 60 * 60,
    });
  }
  if (refreshToken) {
    response.cookies.set("refresh_token", refreshToken, {
      httpOnly: true,
      sameSite: "lax",
      path: "/",
      secure: process.env.NODE_ENV === "production",
      maxAge: 60 * 60 * 24 * 7,
    });
  }
  return response;
}


