# CroqTile · ATC’26 · 13-minute 30-second talk notes

Pacing target: 13:30 total, including slide transitions and brief pauses. The script has approximately 1,931 spoken words; at 150 words per minute, this leaves about 38 seconds for pauses. P1–P6 wording is preserved from the manually polished slides. Timing labels are rehearsal targets.

## P1 · Title · 0:00–0:20

Hi everyone, I am Heng Shi from Enflame Technology and Shanghai Jiao Tong University. I am happy here to present our work on CroqTile, a new GPU programming language designed for autonomous kernel tuning. Let us get start with the motivation.

## P2 · Operator work keeps growing · 0:20–1:15

As you can see in the figures, the bottom one shows the number of works related to operator optimization and kernel tuning, and the the larger figure shows the number of programming models, domain-specific languages, and tools emerged for writing computing kernels.

From the data, we can easily to tell two things, on the one hand, the topic about kernel tuning has draw much attention than ever before, especially for the most recent 2-3 years. On the other hand, recently emerged DSLs seems all have much higher abstraction level for programming.

To me, this two phenomenon reveals one thing. the demand for operator development has largely increased.

Why is that? we know the model architecture are actually converged into several families, like encoder, decoder and diffusion model, so why the operator optimization efforts are somehow increased

## P3 · Why kernels multiply · 1:15–2:15

I think there are four reasons stack together.

Firstly, the operators themselves keep changes. we now have much more variants of one operator than the early year of deep learning. Take attn layers as example, you now have so many variants listed here.

Secondly, we have more hardware platforms than ever before, due to the demand for computing power. just like GPGPU, TPU, PIM, DSA and so many more.

And also, even within the same device itself, it still evolves and changes. This change will lead to things like new HW features, different ISAs, new programming abstractions, and of course different sweet zone for performance.

And lastly, you may notice that the amount of fused operators today are hugely increased with the evolution of AI inference infrastructure

all these together makes the effort for writing computing kernel become so expensive.

## P4 · Kernel optimizations interact · 2:15–3:15

So of course, we would hope kernel tuning itself is not that hard. unfortunately, this is unrealistic. Let's look at how a single kenrel tuned, there will be so many things to consider. locality, bank conflict, instruction spill, memory hierarchy. For these concerns, we then designed many optimization techniques and tricks, like data Tiling, data reuse, swizzling, multibuffering, warp specialization.

So what does a optimised kernel looks like? just like this figure, you would have to find out a recipe of techniques and trick and combine them together, this recipe is never easy to find. because all these factors are coupled together, for example on GPU, a larger tile may improve locality, but can consume more shared memory per block, this will unfortunately limit the parallelism

So you can see, tradeoff is everywhere, so, how do we normally do to find this combination recipe?

## P5 · Bottleneck-driven tuning · 3:15–3:55

The first way is probably familiar to you.

We can simply start from a naive version of implementation, profile it, find out its bottleneck, and pick up a trick for this bottleneck. by make this move iteratively like a loop. you will somehow approach a near-optimal version of kernel.

We can call this bottleneck-first approach or what ever you like. and this i s how human developer normally does. no matter you are an apprentice or experts. Experts may be able to skip iterations, make multiple changes on the kernel and see further, but anyway, they still follow this workflow.

## P6 · Template search · 3:55–5:00

The second way I would like to call it search-based approach. for this way, you will find familiar names, such as autotuning and loop synthesiser. Normally, We would write a template called kernel scheme with tunable parameters, like tile size, stages, and warp count.

As the figure shows, this is a search problem in discrete space, where each point is one concrete kernel implementaion. Having this search space, you can then use algorithms you like to approaching the optimal kernel. you can do genetic search, you can do monte carlo, you can do swarm search.

This method was popular years ago, because they are the automation attempt for tuning kernels to save human efforts before AI agents pops in. and for this purpose, we also created tools for exposing more performance related factors to the syntax, and let you control. The famous name for these tools are halide IR, TVM and we call them scheduling DSL.

## P7 · Compiler transformations · 5:00–5:35

The third way is to put these optimization tricks into the compiler. As you can see here, data tiling becomes loop tiling, data reuse becomes cache staging, and multibuffering becomes software pipelining.

So we can describe a schedule, or let compiler passes apply these transformations. This is where tools like TVM and MLIR come in. But there is still human effort behind it. When new hardware needs a new kernel structure, somebody has to teach the compiler how to make that transformation.

## P8 · Agents rewrite the kernel · 5:35–6:15

So now, with coding agents, we have another way to do this. Remember the bottleneck-first approach? We can put an agent into that loop, let it read the kernel, look at the profiler feedback, and pick up a trick to try.

The agent can change parameters, and also rewrite the kernel structure. Of course, this needs planning, evaluation, tools and knowledge, just like the things listed here. In our work, we focus on the programming language and compiler. How can we make this tuning loop easier for the agent?

## P9 · Design for agent failures · 6:15–7:05

Firstly, let us look at where the agent gets into trouble. I think there are three things to consider.

One is context. Every iteration adds code, profiler output and debugging messages. After several rounds, earlier attempts may get pushed out, so the agent loses track of what it already tried.

Secondly, one optimization can require changes in many places. Take TMA as an example, you have the descriptor, swizzle, copy and synchronization. Miss one, and the kernel may fail.

And lastly, the error may not tell you much. A GPU hang, for example, does not tell the agent which statement to fix.

So we want compact source, fewer coupled edits, and feedback that helps the next repair.

## P10 · CroqTile: two co-design axes · 7:05–7:45

But of course, making the language higher level does not automatically solve this problem. We still need control over the things that affect performance.

CUDA and CuTe give us this control, but there can be a lot of code to maintain. Tile languages make the code shorter, but some structural choices are hidden.

So for CroqTile, we bring two things together. Firstly, design the syntax around the agent's context, so it can keep useful tuning history. Secondly, connect the compiler with the tuning harness, so the agent knows why a candidate failed and what to change.

## P11 · Compact syntax preserves context · 7:45–8:25

Let us look at the first part. I am not going through the whole grammar here, but take the kernel on the bottom left as an example. For the same persistent, warp-specialized GEMM, CroqTile takes 36 lines, and CUDA with CuTe takes 182.

So what does this save for the agent? Counting source, feedback and skills, one static-shape attempt takes about 2,370 tokens, compared with 4,480 for CUDA.

With the same eight-K comparison budget, this leaves 1.6 times as much room for history. So the agent can keep more previous attempts and measurements when deciding what to try next.

## P12 · parallel: one construct, three levels · 8:25–9:05

Now let us see how we expose the performance controls. The first example is parallelism.

As you can see on the right, we use the same parallel construct for blocks, warpgroups and threads. We describe how to divide the work and which level executes it.

Then in the bottom example, we give two warpgroups different jobs. One moves data with TMA, and the other computes with MMA. This gives us the producer-consumer structure.

So when the agent wants to change this structure, there is a clear place to edit, without rebuilding all the thread-index calculations.

## P13 · tma: one statement per transfer · 9:05–9:45

The second example is TMA data movement. Remember that one change could involve several pieces of code?

Here, we describe the transfer in one statement. The source and destination tell us which tile moves where, and the swizzle is a modifier. The compiler then generates the corresponding descriptor.

As you can see, this example takes two statements, one load and one store. We still let the agent choose the swizzle, because it affects performance. The compiler keeps the derived descriptor consistent with that choice. So there are fewer details for the agent to maintain by hand.

## P14 · Compile success across shapes · 9:45–10:20

So does this help the agent produce a program that compiles? Under the same agent, hardware and budget, CroqTile reaches 85.7 percent on the first attempt for static shapes. For dynamic shapes, it stays at 82.1 percent, compared with 48 percent for Triton in this evaluation.

Two things contribute here: fewer coupled edits in the syntax, and symbolic inference to work out shape relationships.

Of course, compiling successfully does not mean the result is correct. We still verify correctness, but fewer compile repairs leave more time for tuning.

## P15 · Diagnostics that guide repair · 10:20–11:05

And when compilation does fail, what should we return to the agent? This brings us to the compiler and harness.

We check shapes and resource limits before launch, and use runtime assertions for constraints that depend on runtime values.

Let us follow the example on the left. The feedback tells us which constraint failed, what values we observed, where the statement is, and how to repair it. Here, the dimensions do not match, and the suggested repair is to add zero fill for the tail tile.

So the agent has a concrete next move: go to that statement, make the change, and compile again.

## P16 · Prune before GPU execution · 11:05–11:45

These checks also help us save GPU trials. We have 353 checks across seven modules. In this sparse GEMM sweep, we start with 480 configurations, and only 102 remain viable. So about 79 percent are pruned before GPU execution, mostly due to register and shared-memory limits.

And the feedback matters for performance too. Replacing structured feedback with generic errors reduces throughput by 14.9 percent in the sparse GEMM ablation.

The reason is that tuning time is limited. More time spent guessing how to fix a program means fewer chances to find a faster kernel.

## P17 · Close the autonomous loop · 11:45–12:25

Now let us put these pieces back into the tuning loop. The agent profiles, proposes a change, implements it, compiles, measures, and decides whether to keep it.

If compilation fails, the feedback goes back for repair. If it passes, we check correctness and measure performance. Skills and references provide the language rules and optimization ideas along the way.

So this is still the iterative workflow we started with. Across the evaluated workloads with vendor references, the resulting kernels achieve a geometric-mean speedup of 1.23 times. Let us look at two examples.

## P18 · Tuning beyond cuBLAS · 12:25–13:00

As you can see on the left, this is dense FP16 GEMM at 16,384 cubed. The solid lines show the best throughput found so far, and the dashed line is cuBLAS. CroqTile gradually improves, reaches that line, and then goes beyond it.

On the right, for block-scale E4M3 GEMM at 8,192 cubed, it crosses the vendor baseline earlier and keeps improving.

Both use the same agent and per-shape time cap on H800. So in these two cases, the agent can keep turning its changes into working, faster kernels.

## P19 · Thank you · 13:00–13:30

So the main idea is to make the language and compiler fit this iterative tuning process. Compact code helps the agent keep its history, explicit controls let it try optimizations, and useful feedback helps it repair mistakes.

CroqTile is open source, and you can see five accepted works using it here. Please feel free to scan the code and have a look.

That is all from me. Thank you, and happy to take your questions.
