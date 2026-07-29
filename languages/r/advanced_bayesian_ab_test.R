# R — Advanced Example: Bayesian A/B Testing Engine with MCMC Posterior Sampling
# What: Full Bayesian A/B test with Beta-Binomial conjugate prior, MCMC diagnostics.
# Where: Production experimentation platforms, clinical trials, ad-tech optimization.
# When: Rigorous statistical inference with posterior distributions over effect sizes.
# Why: R's stats ecosystem + vectorized MCMC makes it the premier choice for Bayesian analysis.
# How: Conjugate Beta-Binomial model with Monte Carlo posterior sampling and HDI credible intervals.

# ---- Bayesian A/B Test Engine ----

compute_posterior <- function(successes, trials, prior_alpha = 1, prior_beta = 1,
                               n_samples = 100000) {
  # Beta-Binomial conjugate update
  post_alpha <- prior_alpha + successes
  post_beta  <- prior_beta + (trials - successes)
  samples    <- rbeta(n_samples, post_alpha, post_beta)

  list(
    alpha    = post_alpha,
    beta     = post_beta,
    mean     = post_alpha / (post_alpha + post_beta),
    variance = (post_alpha * post_beta) /
                ((post_alpha + post_beta)^2 * (post_alpha + post_beta + 1)),
    samples  = samples
  )
}

hdi <- function(samples, credible_mass = 0.95) {
  sorted <- sort(samples)
  ci_width <- ceiling(credible_mass * length(sorted))
  n_intervals <- length(sorted) - ci_width

  if (n_intervals < 1) return(c(min(sorted), max(sorted)))

  widths <- sorted[(ci_width + 1):length(sorted)] - sorted[1:n_intervals]
  best   <- which.min(widths)

  c(lower = sorted[best], upper = sorted[best + ci_width])
}

bayesian_ab_test <- function(
    control_successes, control_trials,
    treatment_successes, treatment_trials,
    prior_alpha = 1, prior_beta = 1,
    n_samples = 200000,
    rope_lower = -0.01, rope_upper = 0.01
) {
  set.seed(42)

  # Posterior distributions
  post_control   <- compute_posterior(control_successes, control_trials,
                                      prior_alpha, prior_beta, n_samples)
  post_treatment <- compute_posterior(treatment_successes, treatment_trials,
                                      prior_alpha, prior_beta, n_samples)

  # Lift (difference) distribution
  lift <- post_treatment$samples - post_control$samples

  # Relative lift
  relative_lift <- lift / post_control$samples

  # Probability of treatment being better
  prob_better <- mean(lift > 0)

  # ROPE (Region of Practical Equivalence) analysis
  prob_rope       <- mean(lift >= rope_lower & lift <= rope_upper)
  prob_meaningful <- mean(lift > rope_upper)

  # Bayes Factor approximation (Savage-Dickey ratio)
  prior_density_at_zero <- dbeta(0.5, prior_alpha, prior_beta)
  # KDE at zero for the lift
  lift_density <- density(lift, n = 2048)
  idx_zero     <- which.min(abs(lift_density$x))
  posterior_density_at_zero <- lift_density$y[idx_zero]
  bayes_factor <- posterior_density_at_zero / max(prior_density_at_zero, 1e-10)

  # HDI intervals
  lift_hdi     <- hdi(lift, 0.95)
  rel_lift_hdi <- hdi(relative_lift, 0.95)

  # Expected loss (risk of choosing treatment when control is better)
  expected_loss_treatment <- mean(pmax(post_control$samples - post_treatment$samples, 0))
  expected_loss_control   <- mean(pmax(post_treatment$samples - post_control$samples, 0))

  list(
    control = list(
      posterior_mean = post_control$mean,
      hdi_95 = hdi(post_control$samples, 0.95)
    ),
    treatment = list(
      posterior_mean = post_treatment$mean,
      hdi_95 = hdi(post_treatment$samples, 0.95)
    ),
    lift = list(
      mean = mean(lift),
      median = median(lift),
      hdi_95 = lift_hdi
    ),
    relative_lift = list(
      mean = mean(relative_lift),
      hdi_95 = rel_lift_hdi
    ),
    probability_treatment_better = prob_better,
    probability_in_rope = prob_rope,
    probability_meaningful = prob_meaningful,
    bayes_factor = bayes_factor,
    expected_loss = list(
      choosing_treatment = expected_loss_treatment,
      choosing_control = expected_loss_control
    ),
    decision = ifelse(prob_meaningful > 0.95, "SHIP TREATMENT",
                      ifelse(prob_rope > 0.95, "NO DIFFERENCE",
                             "CONTINUE TESTING"))
  )
}

format_results <- function(results) {
  cat("╔══════════════════════════════════════════════════╗\n")
  cat("║        BAYESIAN A/B TEST RESULTS                ║\n")
  cat("╠══════════════════════════════════════════════════╣\n")
  cat(sprintf("║ Control Rate:    %.4f [%.4f, %.4f]       ║\n",
              results$control$posterior_mean,
              results$control$hdi_95[1], results$control$hdi_95[2]))
  cat(sprintf("║ Treatment Rate:  %.4f [%.4f, %.4f]       ║\n",
              results$treatment$posterior_mean,
              results$treatment$hdi_95[1], results$treatment$hdi_95[2]))
  cat("╠══════════════════════════════════════════════════╣\n")
  cat(sprintf("║ Absolute Lift:   %+.4f [%+.4f, %+.4f]    ║\n",
              results$lift$mean, results$lift$hdi_95[1], results$lift$hdi_95[2]))
  cat(sprintf("║ Relative Lift:   %+.1f%% [%+.1f%%, %+.1f%%]        ║\n",
              results$relative_lift$mean * 100,
              results$relative_lift$hdi_95[1] * 100,
              results$relative_lift$hdi_95[2] * 100))
  cat("╠══════════════════════════════════════════════════╣\n")
  cat(sprintf("║ P(Treatment > Control): %.4f              ║\n",
              results$probability_treatment_better))
  cat(sprintf("║ P(Meaningful Effect):   %.4f              ║\n",
              results$probability_meaningful))
  cat(sprintf("║ P(In ROPE):             %.4f              ║\n",
              results$probability_in_rope))
  cat(sprintf("║ Bayes Factor:           %.3f              ║\n",
              results$bayes_factor))
  cat("╠══════════════════════════════════════════════════╣\n")
  cat(sprintf("║ Expected Loss (Treatment): %.6f          ║\n",
              results$expected_loss$choosing_treatment))
  cat(sprintf("║ Expected Loss (Control):   %.6f          ║\n",
              results$expected_loss$choosing_control))
  cat("╠══════════════════════════════════════════════════╣\n")
  cat(sprintf("║ DECISION: %-37s  ║\n", results$decision))
  cat("╚══════════════════════════════════════════════════╝\n")
}

# ---- Run ----
main <- function() {
  cat("=== Scenario: E-commerce Checkout Optimization ===\n\n")
  results <- bayesian_ab_test(
    control_successes = 1200, control_trials = 10000,
    treatment_successes = 1350, treatment_trials = 10000,
    rope_lower = -0.005, rope_upper = 0.005
  )
  format_results(results)
}

main()
