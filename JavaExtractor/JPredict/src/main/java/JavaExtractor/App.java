package JavaExtractor;

import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.ThreadPoolExecutor;

import JavaExtractor.Common.Statistics.ContainingNode;
import JavaExtractor.Common.Statistics.InputCategory;
import JavaExtractor.Common.Statistics.OperatorType;
import org.kohsuke.args4j.CmdLineException;

import JavaExtractor.Common.CommandLineValues;
import JavaExtractor.FeaturesEntities.ProgramRelation;

public class App {
	private static CommandLineValues s_CommandLineValues;
	public static List<InputCategory> inputCategories;
	public static List<OperatorType> operatorTypes;
	public static String noBugString = "NoBug";

	public static void main(String[] args) {
		init(args);

		if (s_CommandLineValues.File != null) {
			ExtractFeaturesTask extractFeaturesTask = new ExtractFeaturesTask(s_CommandLineValues,
					s_CommandLineValues.File.toPath());
			extractFeaturesTask.processFile();
		} else if(s_CommandLineValues.Code != null) {
			ExtractFeaturesTask extractFeaturesTask = new ExtractFeaturesTask(s_CommandLineValues);
			extractFeaturesTask.processCode();
		} else if (s_CommandLineValues.Dir != null) {
			extractDir();
		}
	}

	private static void init(String[] args) {
		try {
            s_CommandLineValues = new CommandLineValues(args);
            /*s_CommandLineValues = new CommandLineValues("--max_path_length", "8", "--max_path_width", "2", "--max_contexts", "200", "--dir",  "/home/user/ml4sa_dataset/evaluation/data/");*/
        } catch (CmdLineException e) {
			e.printStackTrace();
			return;
		}

		if (s_CommandLineValues.NoHash) {
			ProgramRelation.setNoHash();
		}

		inputCategories = new ArrayList<>();
		inputCategories.add(new InputCategory(noBugString));
		for (ContainingNode containingNode: ContainingNode.values()) {
			inputCategories.add(new InputCategory(containingNode.toString()));
		}

		operatorTypes = new ArrayList<>();
		for (OperatorType.Type mutationType: OperatorType.Type.values()) {
		    operatorTypes.add(new OperatorType(mutationType));
		}

		clearOutputFiles();
	}

	private static void extractDir() {
		ThreadPoolExecutor executor = (ThreadPoolExecutor) Executors.newFixedThreadPool(s_CommandLineValues.NumThreads);
		LinkedList<ExtractFeaturesTask> tasks = new LinkedList<>();
		try {
			Files.walk(Paths.get(s_CommandLineValues.Dir)).filter(Files::isRegularFile)
					.filter(p -> p.toString().toLowerCase().endsWith(".java")).forEach(f -> {
						ExtractFeaturesTask task = new ExtractFeaturesTask(s_CommandLineValues, f);
						tasks.add(task);
					});
		} catch (IOException e) {
			e.printStackTrace();
			return;
		}
		try {
			executor.invokeAll(tasks);
		} catch (InterruptedException e) {
			e.printStackTrace();
		} finally {
			executor.shutdown();
			printStatistic();
		}
	}

	public static void incrementInputCategory(String category, long inc) {
		inputCategories.stream()
				.filter(ic -> ic.getName().equals(category))
					.forEach(ic -> ic.increment(inc));
	}

	public static void incrementOperatorType(String operator, long inc) {
		operatorTypes.stream()
				.filter(ot -> ot.getType().toString().equals(operator))
				.forEach(ot -> ot.increment(inc));
	}

	private static void printStatistic() {
		StringBuilder sb = new StringBuilder();
		String lineSeparator = System.lineSeparator();
		sb.append("Input Categories").append(lineSeparator);
		for (InputCategory inputCategory: inputCategories) {
		    sb.append("Name: ").append(inputCategory.getName()).append(" count: ").append(inputCategory.getCount())
					.append(lineSeparator);
		}
		sb.append("Operator Types").append(lineSeparator);
		for (OperatorType operatorType : operatorTypes) {
		    sb.append("Name: ").append(operatorType.getType().toString()).append(" count: ").append(operatorType
					.getCount()).append(lineSeparator);
		}
		try	{
			FileWriter fw = new FileWriter(Paths.get(System.getProperty("user.dir"),  "statistics.txt").toString());
			fw.write(sb.toString());
			fw.close();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	private static void clearOutputFiles(){
		try {
			FileWriter fw1 = new FileWriter(Paths.get(System.getProperty("user.dir"),  "newContainingNodes.txt").toString());
			FileWriter fw2 = new FileWriter(Paths.get(System.getProperty("user.dir"),  "statistics.txt").toString());
			fw1.close();
			fw2.close();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
}
