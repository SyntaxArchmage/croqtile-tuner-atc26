# CroqTile · ATC'26 · 14-minute talk notes

Timing includes short pauses and slide changes. Read the paragraphs as the script; bracketed cues are for delivery only. The voice follows the handwritten `../slides-craft/decks/academic/gemmsp-sc26/notes.md`.

Approximately 1,800 spoken words. At 140 words per minute, this leaves about 70 seconds for pauses, pointing, and transitions within the 14-minute slot.

## P1 · Title · 0:00–0:20

Hi everyone, I am Heng Shi, from Shanghai Enflame Intelligence and Shanghai Jiao Tong University. I am happy to be here to present our work on CroqTile, a new GPU programming language designed for autonomous kernel tuning. Let us start with the motivation.

## P2 · Operator work keeps growing · 0:20–0:55

So, model architectures are gradually converging into a few families. But if you work on the kernels underneath, there is more and more work to do, right?

As the top figure shows, new GPU DSLs keep coming out. In our survey, 22 out of 46 appeared in 2025 and 2026. The lower figure shows the same trend for operator optimization papers.

So why does the kernel work keep growing, even when the models look similar?

## P3 · Why kernels multiply · 0:55–1:50

We think there are four reasons, and they stack together.

First, the operators themselves keep changing. Even for attention, we have MHA, MQA, GQA, MLA, and more variants. The model is still a transformer, but the kernel is already different.

Second, we have more hardware platforms. A good kernel for NVIDIA does not automatically become a good kernel for AMD or Ascend.

And even within NVIDIA, the instructions keep changing. We just figured out how to use Hopper's warpgroup MMA, and now Blackwell brings another instruction family and another memory to manage.

Finally, we fuse operators together to avoid intermediate memory traffic. This also creates new kernels.

Together, these make a fixed library of standard operators harder to maintain.

## P4 · Kernel optimizations interact · 1:50–2:30

And for each kernel, there are already so many things to consider. Tiling, data reuse, swizzling, multibuffering, warp specialization, and all these tricks on the left.

Like the right figure shows, applying optimizations can move performance by orders of magnitude. So we really have to do them.

But! They are coupled. A larger tile may improve reuse, but it also takes more shared memory. Then fewer pipeline stages fit, and the overlap changes again.

So the difficulty is figuring out which combination works together. Now, how do we normally do this?

## P5 · Bottleneck-driven tuning · 2:30–3:10

The first way is probably familiar to you.

We run the kernel, profile it, and figure out the bottleneck. Then we choose a structural change, implement it, compile, and measure again. If it helps, we keep it; otherwise, we try something else.

For example, if the tensor cores are waiting for data, we may introduce a producer-consumer pipeline. That can change quite a lot of code.

This is powerful, cause the expert can redesign the kernel. But every round needs someone to interpret the feedback and decide the next change.

## P6 · Template search · 3:10–3:45

The second way is autotuning. We write a template with tunable parameters, like tile size, stages, warp count, and swizzle.

As the figure shows, each point is one configuration. We reject the ones that exceed resource limits, then benchmark the remaining candidates.

But the search stays inside the template. If the better kernel needs a different producer-consumer structure, and we did not expose that choice, the search cannot discover it.

## P7 · Compiler transformations · 3:45–4:15

The third way is to let the compiler do the transformations.

You can see the correspondence here. Tiling becomes a loop transformation, data reuse becomes cache staging, and multibuffering becomes software pipelining.

This is how systems like TVM and MLIR help us. But when a new hardware feature requires a new kernel structure, somebody still has to implement the corresponding transformations.

## P8 · Agents rewrite the kernel · 4:15–4:55

OK, now what we gonna do? Recently, people have started putting coding agents into this loop.

The agent can read the source and profiler feedback, propose a change, and rewrite the kernel. So it can change both the parameters and the structure, much like the expert loop we just saw.

There are many efforts on planning, evaluation, tools, and knowledge, as listed on the right.

For this work, we focus on one question: what kind of programming language and compiler feedback would make this agent more effective? This is where CroqTile comes in.

## P9 · Design for agent failures · 4:55–5:50

So first, let us see where the agent gets into trouble.

One is context pressure. A production kernel can take hundreds of lines, and every round adds source code, profiler output, and debugging messages. Eventually, the earlier attempts get pushed out, even though the agent needs them to understand what it already tried.

Second, one change can touch many places. Enabling TMA may involve the descriptor, the swizzle, the copy, and synchronization. Miss one of them, and you may get an annoying runtime bug.

Third, the feedback itself can be hard to use. A GPU hang tells you very little about which line to fix.

These give us three requirements: compact source, independent primitives, and early feedback that tells the agent how to repair the program.

## P10 · Performance + cheap iteration · 5:50–6:30

But we cannot simply make everything high-level, cause we still want the performance controls.

CUDA and CuTe let us express low-level decisions, but the source can be long and the edits are coupled. Tile languages make common operations much simpler, while some structural choices are hidden behind the abstraction.

So our idea is to keep the important decisions explicit, and make each one compact to express and change.

What I would like to emphasize is that the agent still chooses the design. The language makes it easier to implement correctly.

## P11 · Compact syntax preserves context · 6:30–7:25

Let us see what this looks like. I am not gonna go through the all five constructs on the right, but the lower-left figure gives a concrete example.

For the same persistent, warp-specialized GEMM, CroqTile takes 36 lines, compared with 182 for CUDA with CuTe.

And the upper figure asks what this means inside an agent's context. Counting source, feedback, and skills, one static-shape attempt takes about 2,370 tokens, compared with about 4,480 for CUDA.

Using the same eight-K working set for comparison, this leaves 1.6 times as much room for history. Eight-K here is just a comparison budget.

So the saved space can hold previous attempts and measurements. That is useful information for deciding the next edit.

## P12 · parallel: one construct, three levels · 7:25–8:15

Now let us see two syntax examples. The first one is parallelism.

[Point to the three `parallel` blocks on the right.]

You can see the same construct at three levels: blocks, warpgroups, and threads. We specify how the work is divided and which level executes it.

Then look at the bottom example. We create two warpgroups and give them different jobs. One does the TMA data movement, and the other does the MMA computation. This is the producer-consumer structure we mentioned earlier.

The useful part for tuning is that this decision has an explicit place in the source. The agent can change the parallel structure without reconstructing all the thread-index calculations by hand.

## P13 · tma: one statement per transfer · 8:15–9:05

The second example is data movement. Remember that enabling TMA could require changing several coupled pieces?

Here, one statement describes the transfer. The source and destination tell us which tile moves where, and the swizzle is written as a modifier. The compiler derives the corresponding descriptor and transfer machinery.

[Point to the load, then the store.]

So this example needs two statements, one for loading and one for storing. The comparison on the left shows how much supporting code the other implementations require.

We still expose the performance choice, like which swizzle to use. But the agent does not have to manually keep every derived detail consistent with that choice.

## P14 · Compile success across shapes · 9:05–9:45

So does this actually help the agent write a valid program?

Here we compare compile success under the same agent, hardware, and budget. For static shapes, CroqTile reaches 85.7 percent on the first attempt. For dynamic shapes, it stays at 82.1 percent, while Triton reaches 48 percent in this evaluation.

The symbolic shape system helps here, cause the compiler can infer relationships that would otherwise need more handwritten code.

Correctness still needs verification. But fewer compile repairs leave more budget for performance tuning.

## P15 · Diagnostics that guide repair · 9:45–10:40

And what happens when the program does fail? This is the other half of our design.

The symbolic engine checks shapes and resources before launch. For constraints that depend on runtime values, we also have runtime assertions.

Then the compiler and harness return structured feedback. Let us follow the example on the left.

[Follow the four tagged blocks from top to bottom.]

First, which constraint failed? The source and destination dimensions do not match. Second, what values did we observe? Third, which statement caused it? Finally, how can we repair it?

In this case, the message suggests adding zero fill for the tail tile. So the next edit is concrete. The agent can go directly to that statement, apply the repair, and compile again.

## P16 · Prune before GPU execution · 10:40–11:30

We can also use these checks to avoid wasting GPU trials.

The compiler has 353 checks across seven modules. In this sparse GEMM sweep, we start with 480 configurations, and only 102 remain viable. About 79 percent are pruned before GPU execution, mostly because of register and shared-memory limits.

And the feedback quality matters for the final performance too. In the sparse GEMM ablation, replacing the structured feedback with generic errors reduces throughput by 14.9 percent.

Why would an error message affect throughput? Cause the agent has a limited tuning budget. If it spends that budget guessing how to repair invalid programs, it has fewer chances to find a faster valid one.

## P17 · Close the autonomous loop · 11:30–12:25

Now we can put everything together.

One agent follows these six phases: profile, propose, implement, compile, measure, and decide. If compilation rejects the candidate, the feedback goes straight back to implementation. Once the candidate passes the checks, we verify correctness and measure its performance.

We also provide skills and references, so the agent has the language rules and relevant optimization ideas when it needs them.

Remember the expert loop at the beginning? We are still doing that kind of iterative work. Here, the compact program and actionable feedback help the agent carry it out.

Across the evaluated workloads with vendor references, the resulting kernels achieve a geometric-mean speedup of 1.23 times over the vendor libraries. Let us look at two tuning trajectories.

## P18 · Tuning beyond cuBLAS · 12:25–13:20

On the left is dense FP16 GEMM, with all three dimensions equal to 16,384. The horizontal axis is tuning iteration, and the vertical axis is throughput. The solid lines track the best result found so far.

[Trace the blue curve, then point to the dashed line.]

You can see CroqTile gradually improves, reaches the cuBLAS line, and then goes beyond it.

On the right is block-scale E4M3 GEMM, at 8,192 cubed. Here it crosses the vendor baseline much earlier and keeps improving.

What I would like you to notice is the progress across iterations. In these two cases, the agent can keep turning its proposed changes into working, faster kernels. This is the outcome we want from the language and compiler working together.

## P19 · Thank you · 13:20–14:00

So to wrap up, I would like you to take away two things.

First, compact source with explicit performance controls helps the agent explore kernel designs.

Second, early rejection with a concrete repair helps it use the tuning budget effectively.

CroqTile is open source, with five accepted works using it. Please feel free to scan the code and have a look.

Yeah, that is all from me. Thank you, and happy to take your questions.

---

## Rehearsal notes · not spoken

- Keep the CroqTile tab selected on slides 12 and 13. The script does not require live tab switching.
- Timing checkpoints: start the agent discussion at **4:15**, the syntax examples at **7:25**, diagnostics at **9:45**, and results at **12:25**.
- Pause briefly after “But!” on P4 and before the three failures on P9. On P12, P13, and P15, give the audience time to find the code you are pointing at.
- If rehearsal runs long, shorten P3 to one sentence per reason, omit the eight-K comparison sentence and history ratio on P11, and omit the skills paragraph on P17. These cuts recover roughly 25–30 seconds without losing the main argument.
- The 14-minute schedule is a rehearsal target, including transitions, rather than a measured recording duration.
