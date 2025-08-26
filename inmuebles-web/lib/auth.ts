"use client";
import { setAuthToken } from "./api";

// helpers cookie muy simples
function setCookie(name: string, value: string, days = 7) {
  const expires = new Date(Date.now() + days*864e5).toUTCString();
  document.cookie = `${name}=${value}; Path=/; Expires=${expires}; SameSite=Lax`;
}
function delCookie(name: string) {
  document.cookie = `${name}=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax`;
}
function getCookie(name: string) {
  return document.cookie.split("; ").find(x=>x.startsWith(name+"="))?.split("=")[1] ?? null;
}

export function persistToken(token: string | null) {
  if (typeof window === "undefined") return;
  if (token) {
    localStorage.setItem("auth_token", token);
    setCookie("t", token);               // <-- cookie para middleware
    setAuthToken(token);
  } else {
    localStorage.removeItem("auth_token");
    delCookie("t");
    setAuthToken(undefined);
  }
}

export function loadTokenFromStorage() {
  if (typeof window === "undefined") return null;
  const t = localStorage.getItem("auth_token") || getCookie("t");
  setAuthToken(t ?? undefined);
  return t;
}
