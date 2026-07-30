(module
  (func $guard (param $capability i32) (result i32)
    local.get $capability
    i32.const 0
    i32.gt_s)
  (export "guard" (func $guard)))
