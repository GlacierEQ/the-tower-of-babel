library ieee;
use ieee.std_logic_1164.all;

entity fault_tolerant_voter is
  generic (WIDTH : positive := 32);
  port (
    lane_a   : in  std_logic_vector(WIDTH-1 downto 0);
    lane_b   : in  std_logic_vector(WIDTH-1 downto 0);
    lane_c   : in  std_logic_vector(WIDTH-1 downto 0);
    voted    : out std_logic_vector(WIDTH-1 downto 0);
    mismatch : out std_logic
  );
end entity;

architecture rtl of fault_tolerant_voter is
begin
  voted <= (lane_a and lane_b) or (lane_a and lane_c) or (lane_b and lane_c);
  mismatch <= '0' when lane_a = lane_b and lane_b = lane_c else '1';

  process(lane_a, lane_b, lane_c)
  begin
    assert not (lane_a /= lane_b and lane_a /= lane_c and lane_b /= lane_c)
      report "All three redundant lanes disagree"
      severity warning;
  end process;
end architecture;
