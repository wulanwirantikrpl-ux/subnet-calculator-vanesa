const $ = (id) => document.getElementById(id);

document.querySelectorAll(".tab").forEach((button) => {
  button.addEventListener("click", () => {
    const selected = button.dataset.tab;
    document.querySelectorAll(".tab").forEach((tab) => {
      const active = tab === button;
      tab.classList.toggle("active", active);
      tab.setAttribute("aria-selected", String(active));
    });
    document.querySelectorAll(".panel").forEach((panel) => {
      const active = panel.id === `panel-${selected}`;
      panel.classList.toggle("active", active);
      panel.hidden = !active;
    });
  });
});

function showError(id, message) {
  const box = $(id);
  box.textContent = message;
  box.hidden = false;
}
function clearError(id) { $(id).hidden = true; }
function showEmpty(id, visible) { $(id).hidden = !visible; }

$("subnet-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  clearError("subnet-error");
  $("subnet-result").hidden = true;
  showEmpty("subnet-empty", false);
  const ip = $("ip").value.trim();
  const prefix = $("prefix").value;
  try {
    const response = await fetch(`/api/subnet?ip=${encodeURIComponent(ip)}&prefix=${encodeURIComponent(prefix)}`);
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Perhitungan subnet gagal.");
    $("r-network").textContent = data.network;
    $("r-mask").textContent = data.mask;
    $("r-broadcast").textContent = data.broadcast ?? "Tidak ada (RFC 3021 /32)";
    $("r-hosts").textContent = data.usable_hosts.toLocaleString("id-ID");
    $("r-first").textContent = data.first_host;
    $("r-last").textContent = data.last_host;
    $("r-cidr").textContent = `${ip}/${prefix}`;
    const note = Number(prefix) === 31
      ? "Prefix /31 menggunakan aturan point-to-point RFC 3021: kedua alamat dapat digunakan sebagai host."
      : Number(prefix) === 32
        ? "Prefix /32 menunjukkan satu alamat host tunggal."
        : "Network address diperoleh melalui operasi bitwise AND antara alamat IP dan subnet mask.";
    $("subnet-note").textContent = note;
    $("subnet-result").hidden = false;
  } catch (error) {
    showError("subnet-error", error.message);
    showEmpty("subnet-empty", true);
  }
});

function renumberHosts() {
  document.querySelectorAll(".host-row").forEach((row, index) => {
    row.querySelector(".host-index").textContent = String(index + 1).padStart(2, "0");
    row.querySelector("input").setAttribute("aria-label", `Kebutuhan host ${index + 1}`);
  });
}
$("add-host").addEventListener("click", () => {
  const count = document.querySelectorAll(".host-row").length;
  if (count >= 20) return showError("vlsm-error", "Maksimal 20 kebutuhan host dalam satu perhitungan.");
  const row = document.createElement("div");
  row.className = "host-row";
  row.innerHTML = `<span class="host-index"></span><input type="number" min="1" value="10"><span class="host-unit">HOSTS</span><button type="button" class="remove-host" aria-label="Hapus kebutuhan">×</button>`;
  $("host-list").appendChild(row);
  renumberHosts();
  clearError("vlsm-error");
});
$("host-list").addEventListener("click", (event) => {
  if (!event.target.classList.contains("remove-host")) return;
  if (document.querySelectorAll(".host-row").length <= 1) return showError("vlsm-error", "Minimal harus ada satu kebutuhan host.");
  event.target.closest(".host-row").remove();
  renumberHosts();
});
$("vlsm-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  clearError("vlsm-error");
  $("vlsm-result").hidden = true;
  showEmpty("vlsm-empty", false);
  const requirements = [...document.querySelectorAll(".host-row input")].map((input) => Number(input.value));
  try {
    const response = await fetch("/api/vlsm", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({network: $("vlsm-network").value.trim(), kebutuhan_host: requirements})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Alokasi VLSM gagal.");
    $("vlsm-body").innerHTML = data.map((item, index) => `
      <tr><td>${String(index + 1).padStart(2, "0")}</td>
      <td>${item.kebutuhan.toLocaleString("id-ID")}</td>
      <td>${item.network_cidr}</td>
      <td>${item.first_host} – ${item.last_host}</td>
      <td>${item.usable_hosts.toLocaleString("id-ID")}</td></tr>`).join("");
    $("vlsm-result").hidden = false;
  } catch (error) {
    showError("vlsm-error", error.message);
    showEmpty("vlsm-empty", true);
  }
});

// Hasil contoh langsung tersedia saat halaman dibuka.
$("subnet-form").requestSubmit();
