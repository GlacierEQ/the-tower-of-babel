defmodule ClusterSupervisor do
  use GenServer
  def init(:ok), do: {:ok, %{gpus: 100000}}
end
