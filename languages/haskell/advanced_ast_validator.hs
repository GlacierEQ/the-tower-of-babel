module Main where

import Data.Char (ord)
import Data.List (intercalate)
import Numeric (showHex)

-- A small policy AST for capability-bound agent execution.
data Action
  = ReadArtifact FilePath
  | WriteInternal FilePath
  | InvokeTool String
  | ExternalCall String
  | DeleteArtifact FilePath
  deriving (Eq, Show)

data Policy = Policy
  { allowedTools :: [String]
  , allowedDomains :: [String]
  , writableRoots :: [FilePath]
  , destructiveAllowed :: Bool
  }
  deriving (Eq, Show)

data ValidationError
  = EmptyIdentifier String
  | ToolNotAllowed String
  | DomainNotAllowed String
  | WriteOutsideRoot FilePath
  | DestructiveActionDenied FilePath
  deriving (Eq, Show)

data Decision = Decision
  { accepted :: Bool
  , actionCount :: Int
  , errors :: [ValidationError]
  , receiptHash :: String
  }
  deriving (Eq, Show)

nonEmpty :: String -> Either ValidationError String
nonEmpty value
  | null value = Left (EmptyIdentifier "action field")
  | otherwise = Right value

isPrefixOfPath :: FilePath -> FilePath -> Bool
isPrefixOfPath root path = take (length root) path == root

validateAction :: Policy -> Action -> [ValidationError]
validateAction _ (ReadArtifact path) = either (: []) (const []) (nonEmpty path)
validateAction policy (WriteInternal path)
  | null path = [EmptyIdentifier "write path"]
  | any (`isPrefixOfPath` path) (writableRoots policy) = []
  | otherwise = [WriteOutsideRoot path]
validateAction policy (InvokeTool tool)
  | null tool = [EmptyIdentifier "tool"]
  | tool `elem` allowedTools policy = []
  | otherwise = [ToolNotAllowed tool]
validateAction policy (ExternalCall domain)
  | null domain = [EmptyIdentifier "domain"]
  | domain `elem` allowedDomains policy = []
  | otherwise = [DomainNotAllowed domain]
validateAction policy (DeleteArtifact path)
  | null path = [EmptyIdentifier "delete path"]
  | destructiveAllowed policy = []
  | otherwise = [DestructiveActionDenied path]

-- Deterministic demonstration hash. Production Tower receipts use SHA-256;
-- this exhibit keeps the algorithm dependency-free while preserving the
-- canonicalize -> hash -> receipt architecture.
stableHash :: String -> String
stableHash input =
  let modulus = 4294967291 :: Integer
      step acc char = (acc * 16777619 + toInteger (ord char)) `mod` modulus
      digest = foldl step 2166136261 input
   in pad 8 (showHex digest "")
  where
    pad width value = replicate (max 0 (width - length value)) '0' ++ value

canonicalAction :: Action -> String
canonicalAction (ReadArtifact path) = "read:" ++ path
canonicalAction (WriteInternal path) = "write_internal:" ++ path
canonicalAction (InvokeTool tool) = "tool:" ++ tool
canonicalAction (ExternalCall domain) = "external:" ++ domain
canonicalAction (DeleteArtifact path) = "delete:" ++ path

validatePlan :: Policy -> [Action] -> Decision
validatePlan policy actions =
  let discoveredErrors = concatMap (validateAction policy) actions
      canonical = intercalate "|" (map canonicalAction actions)
   in Decision
        { accepted = null discoveredErrors && not (null actions)
        , actionCount = length actions
        , errors = discoveredErrors
        , receiptHash = stableHash canonical
        }

assert :: String -> Bool -> IO ()
assert label condition =
  if condition
    then putStrLn ("PASS " ++ label)
    else error ("FAILED " ++ label)

main :: IO ()
main = do
  let policy =
        Policy
          { allowedTools = ["tower.validate", "tower.receipt"]
          , allowedDomains = ["api.github.com"]
          , writableRoots = ["build/", "artifacts/"]
          , destructiveAllowed = False
          }
      permitted =
        [ ReadArtifact "registry/tower.yml"
        , InvokeTool "tower.validate"
        , WriteInternal "artifacts/proof.json"
        , ExternalCall "api.github.com"
        ]
      forbidden =
        [ InvokeTool "shell.unbounded"
        , WriteInternal "/etc/passwd"
        , DeleteArtifact "registry/tower.yml"
        ]
      permittedDecision = validatePlan policy permitted
      forbiddenDecision = validatePlan policy forbidden

  assert "permitted plan accepted" (accepted permittedDecision)
  assert "permitted action count" (actionCount permittedDecision == 4)
  assert "receipt is deterministic" (receiptHash permittedDecision == receiptHash (validatePlan policy permitted))
  assert "forbidden plan rejected" (not (accepted forbiddenDecision))
  assert "all forbidden actions explained" (length (errors forbiddenDecision) == 3)
  print permittedDecision
  print forbiddenDecision
