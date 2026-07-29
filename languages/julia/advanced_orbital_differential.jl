using LinearAlgebra
struct State; r::Vector{Float64}; v::Vector{Float64} end
function step(s::State, dt::Float64) return s end
