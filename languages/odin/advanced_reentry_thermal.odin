package thermal
Tile :: struct { temp_k: f64, mach: f64 }
step :: proc(t: ^Tile, dt: f64) { t.temp_k += 14.5 * t.mach * dt }
