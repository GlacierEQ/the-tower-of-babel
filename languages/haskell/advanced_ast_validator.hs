module ASTValidator where
data AST = Action String
validate :: AST -> Bool
validate (Action a) = a /= "DELETE"
