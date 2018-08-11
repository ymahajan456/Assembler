library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;

entity ROM_SIM is
    generic(memory_len : integer := 128 ;
            word_len : integer := 8 ;
            address_len : integer := 32);
    port(
        address0 : in std_logic_vector(address_len -1 downto 0);
        data_out0 : out std_logic_vector(63 downto 0);
        rd0_ena : in std_logic;
        clk : std_logic);
 end entity;

architecture behave of ROM_SIM is
    type int_array is array(0 to memory_len-1) of integer;
    signal memory : int_array := (others => 0);
    constant index_len : integer := integer(ceil(log2(real(memory_len))));
    signal mem_index0  : std_logic_vector(index_len-1 downto 0);
begin
    mem_index0 <= address0(index_len -1 downto 0);
    port0 : process(rd0_ena, mem_index0)
    begin
        data_out0 <= std_logic_vector(to_unsigned(memory(to_integer(unsigned(mem_index0)) + 0),word_len)) & std_logic_vector(to_unsigned(memory(to_integer(unsigned(mem_index0)) + 1),word_len)) & std_logic_vector(to_unsigned(memory(to_integer(unsigned(mem_index0)) + 2),word_len)) & std_logic_vector(to_unsigned(memory(to_integer(unsigned(mem_index0)) + 3),word_len)) & std_logic_vector(to_unsigned(memory(to_integer(unsigned(mem_index0)) + 4),word_len)) & std_logic_vector(to_unsigned(memory(to_integer(unsigned(mem_index0)) + 5),word_len)) & std_logic_vector(to_unsigned(memory(to_integer(unsigned(mem_index0)) + 6),word_len)) & std_logic_vector(to_unsigned(memory(to_integer(unsigned(mem_index0)) + 7),word_len));
    end process;


    memory(0) <= 183;    memory(1) <= 95;    memory(2) <= 148;
    memory(3) <= 120;
end architecture;
