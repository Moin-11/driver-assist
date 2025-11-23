# Test Commands - Driver Assist System

## macOS / Linux

### Brake Events

**Hard Brake:**

```bash
curl -X POST http://localhost:8000/emit \
  -H "Content-Type: application/json" \
  -d '{"module":"Brake Checking","eventType":"hard","force":85,"speed":55,"severity":"high","message":"⚠️ HARD BRAKING DETECTED at 55 mph!"}'
```

**Moderate Brake:**

```bash
curl -X POST http://localhost:8000/emit \
  -H "Content-Type: application/json" \
  -d '{"module":"Brake Checking","eventType":"moderate","force":60,"speed":45,"severity":"moderate","message":"⚡ Moderate braking at 45 mph."}'
```

**Light Brake:**

```bash
curl -X POST http://localhost:8000/emit \
  -H "Content-Type: application/json" \
  -d '{"module":"Brake Checking","eventType":"light","force":25,"speed":30,"severity":"low","message":"✓ Gentle braking at 30 mph."}'
```

---

### Lane Change Events

**Unsafe Lane Change (No Signal):**

```bash
curl -X POST http://localhost:8000/emit \
  -H "Content-Type: application/json" \
  -d '{"module":"Lane Change Detection","eventType":"Center to Right","fromLane":"Center","toLane":"Right","signalUsed":false,"safetyScore":35,"severity":"high","message":"⚠️ Lane change WITHOUT signal! Use turn signals!"}'
```

**Safe Lane Change (With Signal):**

```bash
curl -X POST http://localhost:8000/emit \
  -H "Content-Type: application/json" \
  -d '{"module":"Lane Change Detection","eventType":"Left to Center","fromLane":"Left","toLane":"Center","signalUsed":true,"safetyScore":92,"severity":"low","message":"✓ Safe lane change with signal. Good job!"}'
```

**Dangerous Lane Change:**

```bash
curl -X POST http://localhost:8000/emit \
  -H "Content-Type: application/json" \
  -d '{"module":"Lane Change Detection","eventType":"Right to Left","fromLane":"Right","toLane":"Left","signalUsed":false,"safetyScore":20,"severity":"high","message":"⚠️ DANGEROUS lane change across multiple lanes!"}'
```

---

### GPS Speed Events

**Normal Speed:**

```bash
curl -X POST http://localhost:8000/emit \
  -H "Content-Type: application/json" \
  -d '{"module":"Speed Monitoring","type":"speed_update","speed_mph":45.0,"speed_kph":72.5,"gps_fix":true,"severity":"low","message":"Current speed: 45 mph (73 km/h)"}'
```

**High Speed:**

```bash
curl -X POST http://localhost:8000/emit \
  -H "Content-Type: application/json" \
  -d '{"module":"Speed Monitoring","type":"speed_update","speed_mph":75.0,"speed_kph":120.7,"gps_fix":true,"severity":"moderate","message":"Current speed: 75 mph (121 km/h)"}'
```

---

## Windows (PowerShell)

### Brake Events

**Hard Brake:**

```powershell
Invoke-WebRequest -Uri http://localhost:8000/emit -Method POST -ContentType "application/json" -Body '{"module":"Brake Checking","eventType":"hard","force":85,"speed":55,"severity":"high","message":"HARD BRAKING DETECTED at 55 mph!"}'
```

**Moderate Brake:**

```powershell
Invoke-WebRequest -Uri http://localhost:8000/emit -Method POST -ContentType "application/json" -Body '{"module":"Brake Checking","eventType":"moderate","force":60,"speed":45,"severity":"moderate","message":"Moderate braking at 45 mph."}'
```

**Light Brake:**

```powershell
Invoke-WebRequest -Uri http://localhost:8000/emit -Method POST -ContentType "application/json" -Body '{"module":"Brake Checking","eventType":"light","force":25,"speed":30,"severity":"low","message":"Gentle braking at 30 mph."}'
```

---

### Lane Change Events

**Unsafe Lane Change (No Signal):**

```powershell
Invoke-WebRequest -Uri http://localhost:8000/emit -Method POST -ContentType "application/json" -Body '{"module":"Lane Change Detection","eventType":"Center to Right","fromLane":"Center","toLane":"Right","signalUsed":false,"safetyScore":35,"severity":"high","message":"Lane change WITHOUT signal! Use turn signals!"}'
```

**Safe Lane Change (With Signal):**

```powershell
Invoke-WebRequest -Uri http://localhost:8000/emit -Method POST -ContentType "application/json" -Body '{"module":"Lane Change Detection","eventType":"Left to Center","fromLane":"Left","toLane":"Center","signalUsed":true,"safetyScore":92,"severity":"low","message":"Safe lane change with signal. Good job!"}'
```

**Dangerous Lane Change:**

```powershell
Invoke-WebRequest -Uri http://localhost:8000/emit -Method POST -ContentType "application/json" -Body '{"module":"Lane Change Detection","eventType":"Right to Left","fromLane":"Right","toLane":"Left","signalUsed":false,"safetyScore":20,"severity":"high","message":"DANGEROUS lane change across multiple lanes!"}'
```

---

### GPS Speed Events

**Normal Speed:**

```powershell
Invoke-WebRequest -Uri http://localhost:8000/emit -Method POST -ContentType "application/json" -Body '{"module":"Speed Monitoring","type":"speed_update","speed_mph":45.0,"speed_kph":72.5,"gps_fix":true,"severity":"low","message":"Current speed: 45 mph (73 km/h)"}'
```

**High Speed:**

```powershell
Invoke-WebRequest -Uri http://localhost:8000/emit -Method POST -ContentType "application/json" -Body '{"module":"Speed Monitoring","type":"speed_update","speed_mph":75.0,"speed_kph":120.7,"gps_fix":true,"severity":"moderate","message":"Current speed: 75 mph (121 km/h)"}'
```

**No GPS Fix:**

```powershell
Invoke-WebRequest -Uri http://localhost:8000/emit -Method POST -ContentType "application/json" -Body '{"module":"Speed Monitoring","type":"gps_status","gps_fix":false,"severity":"low","message":"No GPS fix - waiting for satellites"}'
```
