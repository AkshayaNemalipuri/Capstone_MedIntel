function showMessage(element, text, type = "info") {
  element.textContent = text;
  element.className = "message show " + type;
}
function getToken() {
  return localStorage.getItem("medintel_token");
}
function getRole() {
  return localStorage.getItem("medintel_role");
}
function logout() {
  localStorage.removeItem("medintel_token");
  localStorage.removeItem("medintel_role");
  localStorage.removeItem("medintel_user");
  window.location.href = "index.html";
}
async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (options.body && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }
  if (getToken()) headers["Authorization"] = "Bearer " + getToken();
  const response = await fetch(window.MEDINTEL_API + path, { ...options, headers });
  const contentType = response.headers.get("content-type") || "";
  const data = contentType.includes("application/json") ? await response.json() : null;
  if (!response.ok) {
    const detail = data && data.detail;
    throw new Error(typeof detail === "string" ? detail : "Request failed (" + response.status + ")");
  }
  return data;
}
function requireLogin(role) {
  if (!getToken() || getRole() !== role) {
    window.location.href = role === "patient" ? "patient-login.html" : "doctor-login.html";
    return false;
  }
  return true;
}
async function downloadReport(reportId, filename) {
  const response = await fetch(window.MEDINTEL_API + "/reports/" + reportId + "/download", {
    headers: { "Authorization": "Bearer " + getToken() }
  });
  if (!response.ok) {
    alert("Could not download report. Please log in again.");
    return;
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename || "medical-report";
  a.click();
  URL.revokeObjectURL(url);
}
