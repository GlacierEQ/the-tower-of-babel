%%%=============================================================================
%%% @doc
%%% What: Fault-tolerant Tower verification daemon using OTP supervision trees.
%%% Where: Distributed build farms validating Tower artifacts.
%%% When: Robust, always-on, self-healing system requirements.
%%% Why: Let-it-crash philosophy isolates failures, ensuring continuous verification.
%%% How: Implements gen_server for state with ETS persistence, and a one_for_one supervisor.
%%% @end
%%%=============================================================================
-module(advanced_supervisor).
-behaviour(supervisor).
-behaviour(gen_server).

%% API
-export([start_link/0, verify_artifact/1, get_receipt/1]).

%% Supervisor callbacks
-export([init/1]).

%% Gen_server callbacks
-export([init_server/1, handle_call/3, handle_cast/2, handle_info/2, terminate/2, code_change/3]).

%% Supervisor API
start_link() ->
    supervisor:start_link({local, ?MODULE}, ?MODULE, []).

%% Client API
verify_artifact(ArtifactId) ->
    gen_server:cast(tower_receipt_tracker, {verify, ArtifactId}).

get_receipt(ArtifactId) ->
    gen_server:call(tower_receipt_tracker, {get, ArtifactId}).

%% Supervisor callback
init([]) ->
    SupFlags = #{strategy => one_for_one, intensity => 5, period => 10},
    ChildSpecs = [
        #{
            id => tower_receipt_tracker,
            start => {gen_server, start_link, [{local, tower_receipt_tracker}, ?MODULE, server_init, []]},
            restart => permanent,
            shutdown => 5000,
            type => worker,
            modules => [?MODULE]
        }
    ],
    {ok, {SupFlags, ChildSpecs}}.

%% Gen_server callbacks
init_server(server_init) ->
    %% Create ETS table for persistence across crashes
    ets:new(tower_receipts, [set, named_table, public, {read_concurrency, true}]),
    {ok, #{active_tasks => 0}}.

handle_call({get, ArtifactId}, _From, State) ->
    case ets:lookup(tower_receipts, ArtifactId) of
        [{ArtifactId, Receipt}] -> {reply, {ok, Receipt}, State};
        [] -> {reply, not_found, State}
    end.

handle_cast({verify, ArtifactId}, State) ->
    %% Simulate worker task spawning
    spawn(fun() -> 
        %% Simulate work
        timer:sleep(100),
        ets:insert(tower_receipts, {ArtifactId, verified}),
        io:format("Artifact ~p verified~n", [ArtifactId])
    end),
    {noreply, State#{active_tasks := maps:get(active_tasks, State) + 1}}.

handle_info(_Info, State) ->
    {noreply, State}.

terminate(_Reason, _State) ->
    ok.

code_change(_OldVsn, State, _Extra) ->
    {ok, State}.
